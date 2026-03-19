import requests
from bs4 import BeautifulSoup


def scrape_uk():
    print("Checking UK (Contracts Finder)...")

    tenders = []
    base_url = "https://www.contractsfinder.service.gov.uk"

    try:
        url = f"{base_url}/Search/Results?sort=PublishedDate&page=1"
        headers = {"User-Agent": "Mozilla/5.0"}

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
                "url": link
            })

        print(f"UK scraped: {len(tenders)}")

    except Exception as e:
        print("UK scraper error:", e)

    return tenders