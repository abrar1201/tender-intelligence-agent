import requests
from bs4 import BeautifulSoup


def scrape_canada():
    url = "https://buyandsell.gc.ca/procurement-data/tender-notice"

    tenders = []

    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        items = soup.select("a")

        for item in items[:20]:
            title = item.text.strip()
            link = item.get("href")

            if title and link:
                if not link.startswith("http"):
                    link = "https://buyandsell.gc.ca" + link

                tenders.append({
                    "title": title,
                    "description": title,
                    "url": link,
                    "source": "Canada"
                })

    except Exception as e:
        print("Canada scraper error:", e)

    return tenders