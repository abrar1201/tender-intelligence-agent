import requests
from bs4 import BeautifulSoup

URL = "https://www.tenders.gov.au/Atm"


def scrape_austender():

    tenders = []

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        r = requests.get(URL, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        rows = soup.select("table tbody tr")

        for row in rows:

            cols = row.find_all("td")

            if len(cols) < 3:
                continue

            tenders.append({
                "title": cols[1].text.strip(),
                "organization": cols[0].text.strip(),
                "deadline": cols[2].text.strip(),
                "description": cols[1].text.strip(),
                "url": URL
            })

    except Exception as e:
        print("AusTender error:", e)

    print("AusTender scraped:", len(tenders))

    return tenders