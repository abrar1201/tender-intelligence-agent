import requests
import os
from datetime import datetime, timedelta

SAM_API_KEY = os.environ.get("SAM_API_KEY")

def scrape_sam():
    if not SAM_API_KEY:
        print("SAM_API_KEY not found. Skipping SAM.")
        return []

    url = "https://api.sam.gov/opportunities/v2/search"

    params = {
        "api_key": SAM_API_KEY,
        "postedFrom": (datetime.utcnow() - timedelta(days=1)).strftime("%m/%d/%Y"),
        "postedTo": datetime.utcnow().strftime("%m/%d/%Y"),
        "limit": 100
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("SAM API error:", response.status_code)
        print(response.text[:500])
        return []

    try:
        data = response.json()
    except Exception:
        print("SAM returned non-JSON response")
        print(response.text[:500])
        return []

    tenders = []

    if "opportunitiesData" in data:
        for item in data["opportunitiesData"]:
            tenders.append({
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "link": item.get("uiLink"),
                "source": "SAM.gov"
            })

    print(f"SAM scraped: {len(tenders)}")

    return tenders