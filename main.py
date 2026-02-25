import asyncio
from database import init_db, save_tender
from scrapers.uk import scrape_uk
from scrapers.ted import scrape_ted
from scrapers.findatender import scrape_findatender
from ai.embedding import calculate_similarity
from ai.clustering import cluster_tenders
from emailer import send_email

EXCLUDE_KEYWORDS = [
    "laptop", "printer", "equipment",
    "hard drive", "camera", "vehicle",
    "construction", "building", "repair",
    "transport", "furniture"
]


def is_excluded(text):
    text = text.lower()
    return any(word in text for word in EXCLUDE_KEYWORDS)


async def run():
    print("🚀 Starting Procurement Intelligence Bot")

    init_db()

    # Run scrapers in parallel
    uk_task = asyncio.to_thread(scrape_uk)
    ted_task = asyncio.to_thread(scrape_ted)
    fts_task = asyncio.to_thread(scrape_findatender)

    results = await asyncio.gather(uk_task, ted_task, fts_task)

    all_tenders = results[0] + results[1] + results[2]
    print(f"Total scraped: {len(all_tenders)}")

    # Calculate similarity
    for tender in all_tenders:
        tender["similarity"] = calculate_similarity(
            tender["title"] + " " + tender["description"]
        )

    # Apply filtering
    relevant = [
        t for t in all_tenders
        if t["similarity"] > 0.24 and
        not is_excluded(t["title"] + " " + t["description"])
    ]

    print(f"Relevant after filtering: {len(relevant)}")

    if len(relevant) >= 3:
        relevant = cluster_tenders(relevant)

    # Save to DB (optional persistence per run)
    for tender in relevant:
        save_tender(tender)

    print("Saved to SQLite database.")

    # 🔥 SEND EMAIL DIRECTLY FROM LIST
    if relevant:
        send_email(relevant)
    else:
        print("No relevant tenders to email.")

    return relevant


if __name__ == "__main__":
    asyncio.run(run())