import requests

URL = "https://api.sam.gov/prod/opportunities/v2/search"

API_KEY = "SAM-739e5225-39db-4aea-927e-1e47ddcbd2f8"


def scrape_samgov():

    tenders = []

    params = {
        "api_key": API_KEY,
        "limit": 20
    }

    try:

        response = requests.get(URL, params=params)
        data = response.json()

        opportunities = data.get("opportunitiesData", [])

        for item in opportunities:

            tenders.append({
                "title": item.get("title"),
                "organization": item.get("department"),
                "deadline": item.get("responseDeadLine"),
                "description": item.get("description"),
                "url": item.get("uiLink"),
                "source": "samgov"
            })

    except Exception as e:
        print("SAM.gov error:", e)

    print("SAM.gov scraped:", len(tenders))

    return tenders