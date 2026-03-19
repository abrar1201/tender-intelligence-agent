import requests
from bs4 import BeautifulSoup


def scrape_findatender():
    print("Checking Find a Tender Service...")

    tenders = []
    base_url = "https://www.find-tender.service.gov.uk"

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        for page in range(1, 4):  # scrape 3 pages
            print(f"Scraping FTS page {page}...")

            url = f"{base_url}/Search/Results?page={page}"

            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            results = soup.select(".search-result")

            for item in results:
                title_tag = item.select_one("a")
                desc_tag = item.select_one(".search-result-sub-header")

                if not title_tag:
                    continue

                title = title_tag.text.strip()
                link = base_url + title_tag.get("href", "")
                description = desc_tag.text.strip() if desc_tag else ""

                tenders.append({
                    "title": title,
                    "description": description,
                    "url": link,
                    "source": "findatender"   # ✅ ADD THIS
            })

        print(f"FTS scraped total: {len(tenders)}")

    except Exception as e:
        print("FTS error:", e)

    return tenders