import asyncio
import sys
import os
from collections import Counter, defaultdict

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db, save_tender
from portal_db import init_portal_table
from scrapers.uk import scrape_uk
from scrapers.ted import scrape_ted
from scrapers.findatender import scrape_findatender
from scrapers.search_discovery import search_duckduckgo
from scrapers.portal_discovery import discover_portals
from scrapers.portal_crawler import crawl_portals
from ai.embedding import calculate_similarity
from emailer import send_email
from scrapers.samgov import scrape_samgov
from scrapers.worldbank import scrape_worldbank
from scrapers.adb import scrape_adb
from scrapers.austender import scrape_austender
from scrapers.canada import scrape_canada
from scrapers.globaltenders import scrape_globaltenders
from ai.portal_classifier import is_relevant

ENABLE_GLOBAL_DISCOVERY = True


def rank_tenders(tenders):
    return sorted(
        tenders,
        key=lambda x: x.get("similarity") or 0,
        reverse=True
    )


def pick_top_with_source_balance(tenders, total=15, per_source_min=3):
    """
    Guarantees at least `per_source_min` tenders per source,
    then fills remaining slots with highest ranked tenders overall.
    """
    buckets = defaultdict(list)
    for t in tenders:
        buckets[t.get("source", "unknown")].append(t)

    selected = []

    # First pass — guarantee minimum per source
    for source, items in buckets.items():
        selected.extend(items[:per_source_min])

    # Deduplicate preserving order
    seen = set()
    deduped = []
    for t in selected:
        key = t.get("url") or t.get("title")
        if key not in seen:
            seen.add(key)
            deduped.append(t)

    # Second pass — fill remaining slots with highest ranked remaining
    already_selected = {t.get("url") or t.get("title") for t in deduped}
    remaining = [
        t for t in tenders
        if (t.get("url") or t.get("title")) not in already_selected
    ]
    deduped.extend(remaining[:total - len(deduped)])

    return rank_tenders(deduped)[:total]


async def run():
    print("Starting Procurement Intelligence Bot")

    # Initialize DBs
    init_db()
    init_portal_table()

    # Run main scrapers in parallel
    uk_task = asyncio.to_thread(scrape_uk)
    ted_task = asyncio.to_thread(scrape_ted)
    fts_task = asyncio.to_thread(scrape_findatender)

    results = await asyncio.gather(uk_task, ted_task, fts_task)

    all_tenders = results[0] + results[1] + results[2]

    discovered_links = []

    if ENABLE_GLOBAL_DISCOVERY:

        queries = [
            '"ERP implementation tender"',
            '"digital transformation RFP"',
            '"enterprise system procurement"',
            '"Dynamics 365 implementation RFP"',
            '"SAP implementation tender"',
            '"ERP tender site:.gov"',
            '"ERP tender site:.gov.uk"',
            '"ERP tender site:.gov.in"'
        ]

        for q in queries:
            links = search_duckduckgo(q)
            discovered_links.extend(links)

        new_portals = discover_portals(discovered_links)
        print("New portals discovered:", len(new_portals))

        portal_tenders = crawl_portals()
        print("Portal tenders scraped:", len(portal_tenders))

        # all_tenders.extend(portal_tenders)

        print("Checking SAM.gov...")
        all_tenders.extend(scrape_samgov())

        print("Checking World Bank...")
        all_tenders.extend(scrape_worldbank())

        print("Checking Asian Development Bank...")
        all_tenders.extend(scrape_adb())

        print("Checking AusTender...")
        all_tenders.extend(scrape_austender())

        print("Checking Canada Buyandsell...")
        all_tenders.extend(scrape_canada())

        print("Checking GlobalTenders...")
        all_tenders.extend(scrape_globaltenders())

    # Remove tenders with no title and no description
    all_tenders = [
        t for t in all_tenders
        if (t.get("title") or t.get("description"))
    ]

    print(f"\nTotal tenders before filtering: {len(all_tenders)}")

    # STEP 1: Calculate similarity + category
    for tender in all_tenders:
        title = tender.get("title") or ""
        description = tender.get("description") or ""
        text = f"{title} {description}".strip()
        lower_text = text.lower()

        # Category tagging — always runs regardless of similarity
        tender["category"] = [
            k for k in ["erp", "crm", "hcm", "scm", "eam"]
            if k in lower_text
        ]

        if not text:
            tender["similarity"] = None  # None triggers keyword-only path in is_relevant
            continue

        try:
            tender["similarity"] = calculate_similarity(text)
        except Exception as e:
            print(f"Similarity error for '{title[:50]}': {e}")
            tender["similarity"] = None  # None, not 0 — so keyword-only path fires in is_relevant

    # STEP 2: Filter relevant ones
    relevant = [t for t in all_tenders if is_relevant(t)]

    # Debug — source breakdown
    print("\n--- SOURCE BREAKDOWN AFTER FILTER ---")
    source_counts = Counter(t.get("source") for t in relevant)
    print(source_counts)

    print("\n--- UK/FTS SAMPLE ---")
    found_sample = False
    for t in relevant:
        if t.get("source") in ("uk", "findatender"):
            print(f"  source={t.get('source')} | sim={t.get('similarity')} | title={t.get('title', '')[:60]}")
            found_sample = True
    if not found_sample:
        print("  NONE passed the filter")

    print("\n--- TOP 15 SOURCES (before balance) ---")
    top15_unbalanced = rank_tenders(relevant)[:15]
    print(Counter(t.get("source") for t in top15_unbalanced))
    print("--- END DEBUG ---\n")

    # STEP 3: Rank with source balancing — guarantees UK/FTS are represented
    relevant = pick_top_with_source_balance(relevant, total=15, per_source_min=3)

    # STEP 4: Save to DB
    for tender in relevant:
        save_tender(tender)

    print("Saved to database:", len(relevant))
    print("Final source breakdown:", Counter(t.get("source") for t in relevant))

    # STEP 5: Send email
    if relevant:
        send_email(relevant)
    else:
        print("No relevant tenders found.")

    return relevant


if __name__ == "__main__":
    asyncio.run(run())