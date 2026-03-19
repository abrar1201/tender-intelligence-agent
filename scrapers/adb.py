import requests
from bs4 import BeautifulSoup

URL = "https://www.adb.org/work-with-us/procurement"


def scrape_adb():

    tenders = []

    try:

        r = requests.get(URL)
        soup = BeautifulSoup(r.text, "html.parser")

        links = soup.select("a")

        for link in links:

            text = link.text.strip()

            if "tender" in text.lower() or "procurement" in text.lower():

                tenders.append({
                    "title": text,
                    "organization": "Asian Development Bank",
                    "deadline": "",
                    "description": text,
                    "url": link.get("href")
                })

    except Exception as e:
        print("ADB error:", e)

    print("ADB scraped:", len(tenders))

    return tenders