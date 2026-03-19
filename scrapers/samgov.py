import requests
from datetime import datetime, timedelta

URL = "https://api.sam.gov/opportunities/v2/search"
API_KEY = "SAM-739e5225-39db-4aea-927e-1e47ddcbd2f8"

QUERIES = [
    "enterprise resource planning",
    "ERP implementation",
    "CRM system",
    "human capital management",
    "HR management system",
    "payroll system",
    "fleet management system",
    "asset management system",
    "supply chain management",
    "library management system",
    "workforce management",
    "financial management system",
]


def scrape_samgov():
    print("Checking SAM.gov...")
    tenders = []

    today = datetime.today()
    from_date = (today - timedelta(days=90)).strftime("%m/%d/%Y")
    to_date = today.strftime("%m/%d/%Y")

    headers = {
        "X-Api-Key": API_KEY,
        "Accept": "application/json"
    }

    # ✅ Use a session for connection reuse — faster and avoids hanging
    session = requests.Session()
    session.headers.update(headers)

    for query in QUERIES:
        try:
            print(f"  SAM.gov querying: {query}")
            params = {
                "q": query,
                "limit": 10,
                "offset": 0,
                "postedFrom": from_date,
                "postedTo": to_date,
                "ptype": "o",
            }

            # ✅ Strict timeout — (connect timeout, read timeout)
            response = session.get(URL, params=params, timeout=(5, 10))

            if response.status_code == 401:
                print("SAM.gov: API key invalid or not yet active")
                return []

            if response.status_code == 403:
                print("SAM.gov: Access forbidden — check API key permissions at sam.gov")
                return []

            if response.status_code != 200:
                print(f"  SAM.gov {response.status_code} for '{query}': {response.text[:150]}")
                continue

            data = response.json()
            opportunities = data.get("opportunitiesData", [])
            print(f"  SAM.gov '{query}' → {len(opportunities)} results")

            for item in opportunities:
                tenders.append({
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "organization": item.get("department", ""),
                    "deadline": item.get("responseDeadLine", ""),
                    "url": item.get("uiLink") or f"https://sam.gov/opp/{item.get('noticeId', '')}/view",
                    "source": "samgov"
                })

        except requests.exceptions.ConnectTimeout:
            print(f"  SAM.gov connect timeout for '{query}' — skipping")
            continue
        except requests.exceptions.ReadTimeout:
            print(f"  SAM.gov read timeout for '{query}' — skipping")
            continue
        except Exception as e:
            print(f"  SAM.gov error for '{query}':", e)
            continue

    session.close()

    # Deduplicate by URL
    seen = set()
    unique = []
    for t in tenders:
        key = t.get("url") or t.get("title")
        if key not in seen:
            seen.add(key)
            unique.append(t)

    print(f"SAM.gov scraped: {len(unique)}")
    return unique