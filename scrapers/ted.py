import requests

URL = "https://api.ted.europa.eu/v3/notices/search"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

QUERIES = [
    'FT~"enterprise resource planning" AND notice-type=cn-standard',
    'FT~"ERP implementation" AND notice-type=cn-standard',
    'FT~"CRM system" AND notice-type=cn-standard',
    'FT~"human capital management" AND notice-type=cn-standard',
    'FT~"HR management system" AND notice-type=cn-standard',
    'FT~"payroll system" AND notice-type=cn-standard',
    'FT~"fleet management system" AND notice-type=cn-standard',
    'FT~"asset management system" AND notice-type=cn-standard',
    'FT~"supply chain management" AND notice-type=cn-standard',
    'FT~"library management system" AND notice-type=cn-standard',
    'FT~"workforce management" AND notice-type=cn-standard',
    'FT~"financial management system" AND notice-type=cn-standard',
    'FT~"dynamics 365" AND notice-type=cn-standard',
    'FT~"SAP implementation" AND notice-type=cn-standard',
]


def scrape_ted():
    print("Checking TED (EU)...")
    tenders = []

    for query in QUERIES:
        try:
            # ✅ Removed sortField and sortOrder — not supported by this endpoint
            payload = {
                "query": query,
                "fields": ["ND", "TI", "AU", "PD"],
                "page": 1,
                "limit": 10
            }

            res = requests.post(URL, json=payload, headers=HEADERS, timeout=15)

            if res.status_code != 200:
                print(f"TED error {res.status_code} for query '{query[:50]}': {res.text[:200]}")
                continue

            data = res.json()
            notices = data.get("notices", []) or data.get("results", [])

            for item in notices:
                notice_id = item.get("ND", "")
                title = item.get("TI", "No title")
                authority = item.get("AU", "")

                # TED returns fields as dicts with language keys e.g. {"ENG": "..."}
                if isinstance(title, dict):
                    title = title.get("ENG") or next(iter(title.values()), "No title")

                if isinstance(authority, dict):
                    authority = authority.get("ENG") or next(iter(authority.values()), "")

                url = f"https://ted.europa.eu/en/notice/{notice_id}" if notice_id else ""

                tenders.append({
                    "title": title,
                    "description": f"Contracting authority: {authority}" if authority else "",
                    "url": url,
                    "source": "ted"
                })

        except Exception as e:
            print(f"TED error for query '{query[:50]}':", e)

    # Deduplicate by URL
    seen = set()
    unique = []
    for t in tenders:
        key = t.get("url") or t.get("title")
        if key not in seen:
            seen.add(key)
            unique.append(t)

    print(f"TED scraped: {len(unique)}")
    return unique