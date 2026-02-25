import requests
from bs4 import BeautifulSoup


def scrape_findatender():
    print("Checking Find a Tender Service...")

    base_url = "https://www.find-tender.service.gov.uk"
    search_url = f"{base_url}/Search/Results"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    tenders = []

    try:
        #LOOP THROUGH MULTIPLE PAGES
        for page in range(1, 6):   # pages 1 to 5
            print(f"Scraping FTS page {page}...")

            params = {
                "keyword": "ERP OR SAP OR digital transformation OR enterprise system",
                "page": page
            }

            response = requests.get(search_url, params=params, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")

            results = soup.select(".search-result")

            if not results:
                print("No more results found.")
                break

            for r in results:
                title_tag = r.select_one("h2 a")
                if not title_tag:
                    continue

                href = title_tag["href"]
                clean_href = href.split("?")[0]

                if clean_href.startswith("http"):
                    link = clean_href
                else:
                    link = base_url + clean_href

                tenders.append({
                    "title": title_tag.text.strip(),
                    "description": title_tag.text.strip(),
                    "link": link,
                    "source": "UK-FTS"
                })

        print(f"FTS scraped total: {len(tenders)}")
        return tenders

    except Exception as e:
        print("FTS error:", e)
        return []
