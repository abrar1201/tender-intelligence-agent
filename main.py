import asyncio
import sys
import os
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db, save_tender
from portal_db import init_portal_table
from scrapers.uk import scrape_uk
from scrapers.ted import scrape_ted
from scrapers.findatender import scrape_findatender
from scrapers.search_discovery import search_duckduckgo
from scrapers.portal_discovery import discover_portals
from scrapers.portal_crawler import crawl_portals
from ai.embedding import calculate_similarity_with_reason
from emailer import send_email
from scrapers.samgov import scrape_samgov
from scrapers.worldbank import scrape_worldbank
from scrapers.adb import scrape_adb
from scrapers.austender import scrape_austender
from scrapers.canada import scrape_canada
from scrapers.globaltenders import scrape_globaltenders
from ai.portal_classifier import is_relevant

ENABLE_GLOBAL_DISCOVERY = True
MAX_SCRAPER_WORKERS = 8
SCRAPER_TIMEOUT = 90   # per-scraper timeout in seconds


def rank_tenders(tenders):
    return sorted(tenders, key=lambda x: x.get("similarity") or 0, reverse=True)


def deduplicate(tenders):
    seen_urls, seen_titles, unique = set(), set(), []
    for t in tenders:
        url = (t.get("url") or "").strip().lower()
        title = (t.get("title") or "").strip().lower()
        if url and url in seen_urls:
            continue
        if title and title in seen_titles:
            continue
        if url:
            seen_urls.add(url)
        if title:
            seen_titles.add(title)
        unique.append(t)
    return unique


def pick_top_with_source_balance(tenders, total=15, per_source_min=3):
    buckets = defaultdict(list)
    for t in tenders:
        buckets[t.get("source", "unknown")].append(t)

    selected = []
    for source, items in buckets.items():
        selected.extend(items[:per_source_min])

    seen = set()
    deduped = []
    for t in selected:
        key = t.get("url") or t.get("title")
        if key not in seen:
            seen.add(key)
            deduped.append(t)

    already = {t.get("url") or t.get("title") for t in deduped}
    remaining = [t for t in tenders if (t.get("url") or t.get("title")) not in already]
    deduped.extend(remaining[:total - len(deduped)])
    return rank_tenders(deduped)[:total]


# ─────────────────────────────────────────────────────────────────────────────
# PARALLEL SCRAPERS
#
# Uses as_completed with a per-future timeout.
# Each future gets its OWN timeout — one slow scraper never kills the rest.
# executor.map timeout is total-batch which is why it failed before.
# ─────────────────────────────────────────────────────────────────────────────

SCRAPERS = {
    "uk":            scrape_uk,
    "findatender":   scrape_findatender,
    "ted":           scrape_ted,
    "samgov":        scrape_samgov,
    # "worldbank":     scrape_worldbank,
    # "adb":           scrape_adb,
    # "austender":     scrape_austender,
    "canada":        scrape_canada,
    "globaltenders": scrape_globaltenders,
}


def run_scrapers_parallel() -> list:
    all_tenders = []
    start = time.time()
    print("Running scrapers in parallel...")

    with ThreadPoolExecutor(max_workers=MAX_SCRAPER_WORKERS) as executor:
        # Submit all scrapers — each runs independently in its own thread
        future_to_name = {
            executor.submit(fn): name
            for name, fn in SCRAPERS.items()
        }

        # Collect results as they finish — no shared timeout
        # Each future.result() call has its own per-scraper timeout
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                # Per-future timeout — only THIS scraper is cancelled on timeout
                result = future.result(timeout=SCRAPER_TIMEOUT)
                count = len(result) if result else 0
                print(f"  [{name}] {count} tenders")
                if result:
                    all_tenders.extend(result)
            except TimeoutError:
                print(f"  [{name}] TIMEOUT after {SCRAPER_TIMEOUT}s — skipped, others continue")
            except Exception as e:
                print(f"  [{name}] ERROR: {e}")

    print(f"Scrapers done in {time.time() - start:.1f}s — {len(all_tenders)} total")
    return all_tenders


# ─────────────────────────────────────────────────────────────────────────────
# PARALLEL SCORING
# Uses as_completed — each scoring job is independent.
# Results collected into a dict keyed by tender id to preserve all results.
# ─────────────────────────────────────────────────────────────────────────────

def _score_single(tender: dict) -> dict:
    title = tender.get("title") or ""
    description = tender.get("description") or ""
    text = f"{title} {description}".strip()
    lower = text.lower()

    tender["category"] = [k for k in ["erp", "crm", "hcm", "scm", "eam"] if k in lower]

    if not text:
        tender["similarity"] = None
        tender["match_reason"] = "empty"
        return tender

    try:
        score, reason = calculate_similarity_with_reason(text)
        tender["similarity"] = score
        tender["match_reason"] = reason
    except Exception as e:
        tender["similarity"] = None
        tender["match_reason"] = f"error:{e}"

    return tender


def score_tenders_parallel(tenders: list) -> list:
    print(f"Scoring {len(tenders)} tenders in parallel...")
    start = time.time()

    # Use index as key so we can reassemble in order if needed
    scored_map = {}

    with ThreadPoolExecutor(max_workers=MAX_SCRAPER_WORKERS) as executor:
        future_to_idx = {
            executor.submit(_score_single, t): i
            for i, t in enumerate(tenders)
        }

        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                scored_map[idx] = future.result(timeout=10)
            except Exception as e:
                # Keep original tender with None score — never lose a tender
                t = tenders[idx]
                t["similarity"] = None
                t["match_reason"] = f"scoring failed: {e}"
                scored_map[idx] = t

    # Reassemble in original order
    scored = [scored_map[i] for i in range(len(tenders))]

    missing = sum(1 for t in scored if "similarity" not in t)
    if missing:
        print(f"WARNING: {missing} tenders missing similarity key")

    print(f"Scoring done in {time.time() - start:.1f}s")
    return scored


async def run():
    print("Starting Procurement Intelligence Bot")
    print("=" * 50)

    init_db()
    init_portal_table()

    # Step 1 — parallel scraping
    loop = asyncio.get_event_loop()
    all_tenders = await loop.run_in_executor(None, run_scrapers_parallel)

    # Step 2 — optional discovery
    if ENABLE_GLOBAL_DISCOVERY:
        queries = [
            '"ERP implementation tender"',
            '"enterprise resource planning software procurement"',
            '"HR management system tender"',
            '"fleet management software RFP"',
            '"payroll system implementation tender"',
        ]
        discovered_links = []
        for q in queries:
            try:
                links = search_duckduckgo(q)
                discovered_links.extend(links)
            except Exception as e:
                print(f"Discovery query failed: {e}")

        try:
            new_portals = discover_portals(discovered_links)
            print(f"New portals discovered: {len(new_portals)}")
        except Exception as e:
            print(f"Portal discovery failed: {e}")

        try:
            portal_tenders = crawl_portals()
            print(f"Portal tenders scraped: {len(portal_tenders)}")
        except Exception as e:
            print(f"Portal crawl failed: {e}")

    # Step 3 — clean + dedup
    all_tenders = [t for t in all_tenders if t.get("title") or t.get("description")]
    before = len(all_tenders)
    all_tenders = deduplicate(all_tenders)
    print(f"\nAfter dedup: {len(all_tenders)} (removed {before - len(all_tenders)} duplicates)")

    # Step 4 — score in parallel
    all_tenders = await loop.run_in_executor(None, score_tenders_parallel, all_tenders)

    scored_count = sum(1 for t in all_tenders if t.get("similarity") is not None)
    print(f"Scored: {scored_count}/{len(all_tenders)} tenders")

    # Step 5 — filter
    relevant = [t for t in all_tenders if is_relevant(t)]

    print(f"\n--- SOURCE BREAKDOWN AFTER FILTER ---")
    print(Counter(t.get("source") for t in relevant))
    print(f"Total relevant: {len(relevant)}")

    # Step 6 — rank + balance
    relevant = pick_top_with_source_balance(relevant, total=15, per_source_min=3)

    print(f"\n--- FINAL 15 ---")
    for t in relevant:
        sim = t.get("similarity") or 0
        reason = (t.get("match_reason") or "")[:70]
        print(f"  [{t.get('source')}] {sim:.3f} | {t.get('title', '')[:55]}")
        if reason:
            print(f"           {reason}")

    # Step 7 — save + email
    for tender in relevant:
        save_tender(tender)

    print(f"\nSaved: {len(relevant)}")
    print("Final sources:", Counter(t.get("source") for t in relevant))

    if relevant:
        send_email(relevant)
    else:
        print("No relevant tenders found.")

    return relevant


if __name__ == "__main__":
    asyncio.run(run())