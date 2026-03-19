import requests


def scrape_ted():
    print("Checking TED (EU)...")

    tenders = []

    try:
        url = "https://ted.europa.eu/api/v2/notices/search"

        params = {
            "limit": 20,
            "sort": "publication-date-desc"
        }

        res = requests.get(url, params=params, timeout=10)

        if res.status_code != 200:
            print("TED API failed")
            return []

        data = res.json()

        for item in data.get("results", []):
            title = item.get("title", "No title")
            description = item.get("shortDescription", "")
            link = item.get("url", "")

            tenders.append({
                "title": title,
                "description": description,
                "url": link
            })

        print(f"TED scraped: {len(tenders)}")

    except Exception as e:
        print("TED error:", e)

    return tenders