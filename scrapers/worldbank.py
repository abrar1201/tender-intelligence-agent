import requests

URL = "https://search.worldbank.org/api/v2/wds"


def scrape_worldbank():

    tenders = []

    params = {
        "qterm": "procurement",
        "rows": 50
    }

    try:

        r = requests.get(URL, params=params)
        data = r.json()

        docs = data.get("documents", {})

        for item in docs.values():

            tenders.append({
                "title": item.get("display_title"),
                "organization": "World Bank",
                "deadline": "",
                "description": item.get("docdt"),
                "url": item.get("url"),
                "source": "worldbank"
            })

    except Exception as e:
        print("World Bank error:", e)

    print("WorldBank scraped:", len(tenders))

    return tenders