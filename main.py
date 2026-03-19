import asyncio
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

ENABLE_GLOBAL_DISCOVERY = True


def rank_tenders(tenders):
    return sorted(
        tenders,
        key=lambda x: x.get("similarity", 0),
        reverse=True
    )


async def run():
    print("Starting Procurement Intelligence Bot")

    # Initialize DBs
    init_db()
    init_portal_table()

    # Run main scrapers in parallel
    uk_task = asyncio.to_thread(scrape_uk)
    ted_task = asyncio.to_thread(scrape_ted)
    fts_task = asyncio.to_thread(scrape_findatender)

    results = await asyncio.gather(
        uk_task,
        ted_task,
        fts_task
    )

    all_tenders = results[0] + results[1] + results[2]

    discovered_links = []

    # Global discovery 
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

    # STEP 1: Calculate similarity
    for tender in all_tenders:

        text = (
            tender.get("title", "") + " " +
            tender.get("description", "")
        )

        try:
            tender["similarity"] = calculate_similarity(text)
        except Exception as e:
            print("Similarity error:", e)
            tender["similarity"] = 0

    # STEP 2: Filter relevant ones
    relevant = [
        t for t in all_tenders
        if t.get("similarity", 0) > 0.25
    ]

    # STEP 3: Rank tenders
    relevant = rank_tenders(relevant)

    # STEP 4: Take top 15
    relevant = relevant[:15]

    # STEP 5: Save to DB
    for tender in relevant:
        save_tender(tender)

    print("Saved to database:", len(relevant))

    # STEP 6: Send email
    if relevant:
        send_email(relevant)
    else:
        print("No relevant tenders found.")

    return relevant


if __name__ == "__main__":
    asyncio.run(run())