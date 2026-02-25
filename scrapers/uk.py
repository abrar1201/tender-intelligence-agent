import requests
from bs4 import BeautifulSoup

def scrape_uk():
    print("Checking UK (Contracts Finder)...")

    url = "https://www.contractsfinder.service.gov.uk/Search/Results"
    params = {"keyword": "software IT ERP CRM EAM"}
    headers = {"User-Agent": "Mozilla/5.0"}

    tenders = []

    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        results = soup.select(".search-result")

        for r in results[:20]:
            title_tag = r.select_one("h2 a")
            if not title_tag:
                continue

            link = title_tag["href"]
            if link.startswith("/"):
                link = "https://www.contractsfinder.service.gov.uk" + link

            tenders.append({
                "title": title_tag.text.strip(),
                "description": title_tag.text.strip(),
                "link": link,
                "source": "UK"
            })

        print(f"UK scraped: {len(tenders)}")
        return tenders

    except Exception as e:
        print("UK scraper error:", e)
        return []
