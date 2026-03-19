import requests

URL = "https://api.sam.gov/prod/opportunities/v2/search"

API_KEY = "YOUR_SAM_API_KEY"


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
                "url": item.get("uiLink")
            })

    except Exception as e:
        print("SAM.gov error:", e)

    print("SAM.gov scraped:", len(tenders))

    return tenders