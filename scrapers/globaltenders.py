import requests
from bs4 import BeautifulSoup

def scrape_globaltenders():

    print("Checking GlobalTenders...")

    url = "https://www.globaltenders.com/free-global-tenders/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    tenders = []

    try:

        r = requests.get(url, headers=headers, timeout=30)

        soup = BeautifulSoup(r.text, "html.parser")

        rows = soup.select("table tr")

        current = {}

        for row in rows:

            cols = row.find_all("td")

            if len(cols) != 2:
                continue

            key = cols[0].text.strip()
            val = cols[1].text.strip()

            if key == "Notice Type:":
                current = {"title": val}

            if key == "Authority:" and current:
                current["authority"] = val

            if key == "Country:" and current:
                current["country"] = val

            if key == "Document Ref. No:" and current:
                tenders.append({
                    "title": current.get("title", ""),
                    "country": current.get("country", ""),
                    "url": url
                })
                current = {}

        print("GlobalTenders scraped:", len(tenders))

        return tenders

    except Exception as e:

        print("GlobalTenders error:", e)

        return []