import requests

def scrape_ted():
    print("Checking TED via EU Open Data API...")

    url = "https://data.europa.eu/api/hub/search/search"

    params = {
        "q": "ERP OR digital transformation OR enterprise system",
        "fq": "dataset_id:ted-csv",
        "rows": 50
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print("TED API error:", response.status_code)
            return []

        data = response.json()

        tenders = []

        for doc in data.get("result", {}).get("results", []):
            tenders.append({
                "title": doc.get("title", ""),
                "description": doc.get("description", ""),
                "link": doc.get("url", ""),
                "source": "TED EU"
            })

        print(f"TED scraped: {len(tenders)}")
        return tenders

    except Exception as e:
        print("TED error:", e)
        return []