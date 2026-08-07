import requests
from bs4 import BeautifulSoup
import time
import json


def scrape_procontract(pages: int = 5, keyword: str = "") -> list[dict]:
    """
    Scrape public tender opportunities from ProContract (Due North / Proactis).
    Source: https://procontract.due-north.com/Opportunities

    NO LOGIN REQUIRED — the opportunities list is publicly accessible.

    Confirmed table structure (from live HTML):
        Col 0: Title (with <a> link to /Advert?advertId=...)
        Col 1: Buyer (organisation name)
        Col 2: Expression Start  (dd/mm/yyyy)
        Col 3: Expression End    (dd/mm/yyyy)
        Col 4: Estimated Value

    Pagination: Page=N&PageSize=20 GET params.
    Covers 400+ UK public sector organisations (councils, NHS, housing, etc.)

    Args:
        pages:   Number of pages to scrape (20 tenders/page, default 5 = 100).
        keyword: Optional case-insensitive title filter.

    Returns:
        List of dicts: title, buyer, expression_start, deadline,
                       estimated_value, url, source
    """
    print("Checking ProContract (procontract.due-north.com)...")

    tenders = []
    base_url = "https://procontract.due-north.com"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Referer": f"{base_url}/Opportunities",
    }

    session = requests.Session()

    # Warm up — establishes session cookie (ASP.NET_SessionId required)
    try:
        session.get(f"{base_url}/Opportunities", headers=headers, timeout=15)
        time.sleep(0.5)
    except Exception as e:
        print(f"  ProContract: warm-up failed: {e}")

    for page in range(1, pages + 1):
        print(f"  Scraping ProContract page {page}...")

        # Sort by ExpressionEndDate Descending = most recently closing first
        # PageSize=20 confirmed available from pager links in live HTML
        url = (
            f"{base_url}/Opportunities/Index"
            f"?Page={page}"
            f"&PageSize=20"
            f"&SortColumn=ExpressionEndDate"
            f"&SortDirection=Descending"
            f"&tabname=opportunities"
        )

        try:
            res = session.get(url, headers=headers, timeout=15)
            res.raise_for_status()
        except requests.RequestException as e:
            print(f"  ProContract page {page} error: {e}")
            break

        page_tenders = _parse_procontract_table(res.text, base_url, keyword)

        if not page_tenders:
            print(f"  ProContract page {page}: no results, stopping.")
            break

        tenders.extend(page_tenders)
        print(f"  ProContract page {page}: {len(page_tenders)} tenders.")
        time.sleep(1)

    print(f"ProContract scraped total: {len(tenders)} tenders.")
    return tenders


def _parse_procontract_table(html: str, base_url: str, keyword: str = "") -> list[dict]:
    """
    Parse the opportunities table from ProContract.

    The table has <thead> with sortable column headers and <tbody> rows.
    Confirmed column order: Title | Buyer | Expression Start | Expression End | Estimated Value
    """
    soup = BeautifulSoup(html, "html.parser")
    tenders = []

    # Find the results table — confirmed header: "Title", "Buyer", "Expression Start"
    target_table = None
    for table in soup.find_all("table"):
        header_text = table.get_text(" ", strip=True)
        if "Expression Start" in header_text and "Expression End" in header_text:
            target_table = table
            break

    if not target_table:
        return tenders

    rows = target_table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")

        # Need 5 columns; skip <th> header rows
        if len(cols) < 4:
            continue

        # ── Col 0: Title + link ─────────────────────────────────────────
        a_tag = cols[0].find("a")
        if not a_tag:
            continue

        title = a_tag.get_text(separator=" ", strip=True)
        if not title:
            continue

        href = a_tag.get("href", "")
        url = href if href.startswith("http") else (base_url + href if href else "")

        # The title attr on the <a> contains the DN reference number
        dn_ref = a_tag.get("title", "").strip()

        # ── Col 1: Buyer ────────────────────────────────────────────────
        buyer = cols[1].get_text(separator=" ", strip=True)

        # ── Col 2: Expression Start ─────────────────────────────────────
        expression_start = cols[2].get_text(strip=True)

        # ── Col 3: Expression End (deadline) ────────────────────────────
        deadline = cols[3].get_text(strip=True)

        # ── Col 4: Estimated Value ──────────────────────────────────────
        estimated_value = cols[4].get_text(strip=True) if len(cols) > 4 else ""

        # ── Optional keyword filter ─────────────────────────────────────
        if keyword and keyword.lower() not in title.lower():
            continue

        tenders.append({
            "title": title,
            "description": f"{buyer} — {dn_ref}".strip(" —"),  # enriches scorer
            "reference": dn_ref,
            "buyer": buyer,
            "organisation": buyer,           # used by emailer
            "expression_start": expression_start,
            "deadline": deadline,
            "estimated_value": estimated_value,
            "value": estimated_value,        # used by emailer
            "url": url,
            "source": "procontract",
        })

    return tenders


if __name__ == "__main__":
    results = scrape_procontract(pages=2)
    for r in results[:5]:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    print(f"\nTotal: {len(results)}")
    
    