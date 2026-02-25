import asyncio
from database import init_db, save_tender
from scrapers.uk import scrape_uk
from scrapers.ted import scrape_ted
from scrapers.findatender import scrape_findatender
from ai.embedding import calculate_similarity
from ai.clustering import cluster_tenders


#Exclusion filter (removes hardware & irrelevant tenders)
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
    print("Starting Procurement Intelligence Bot")

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

    # Apply similarity + exclusion filtering
    relevant = [
        t for t in all_tenders
        if t["similarity"] > 0.24 and
        not is_excluded(t["title"] + " " + t["description"])
    ]

    print(f"Relevant after filtering: {len(relevant)}")

    # Cluster if enough tenders
    if len(relevant) >= 3:
        relevant = cluster_tenders(relevant)
    else:
        print("Not enough tenders to cluster.")

    print(f"Final relevant tenders: {len(relevant)}")

    # Save to DB
    for tender in relevant:
        save_tender(tender)

    print("Saved to SQLite database.")
    return relevant


if __name__ == "__main__":
    asyncio.run(run())

    # 🔹 Show Top Results
    import sqlite3

    conn = sqlite3.connect("tenders.db")
    c = conn.cursor()

    c.execute("""
        SELECT title, similarity, link
        FROM tenders
        ORDER BY similarity DESC
        LIMIT 10
    """)

    rows = c.fetchall()

    print("\nTop ERP-Relevant Tenders:")
    for r in rows:
        print(f"\n{r[0]}")
        print(f"Score: {r[1]:.3f}")
        print(f"Link: {r[2]}")

    conn.close()
