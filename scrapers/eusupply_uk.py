import requests
from bs4 import BeautifulSoup
import time
import json


def scrape_eusupply_uk(pages: int = 4, keyword: str = "") -> list[dict]:
    """
    Scrape public tenders from eu-supply.com (UK instance).
    Source: https://uk.eu-supply.com/ctm/supplier/publictenders?B=UK

    Confirmed table structure (from live HTML, 25 rows/page):
        Col 0: Quote/Tender ID
        Col 1: Reference
        Col 2: Name (with <a> link)
        Col 3: Date of Publication  (dd/mm/yyyy)
        Col 4: Response Deadline    (dd/mm/yyyy HH:MM)
        Col 5: Process / Procedure
        Col 6: Buyers (Contracting Authority)
        Col 7: Countries

    Pagination: /ctm/supplier/publictenders/<page_number>?B=UK
    Page 1 = base URL, Page 2 = /ctm/supplier/2, etc.

    Args:
        pages:   Number of pages to scrape (25 tenders/page, default 4 = 100).
        keyword: Optional case-insensitive title filter.

    Returns:
        List of dicts: title, reference, tender_id, buyer, procedure,
                       date_published, deadline, country, url, source
    """
    print("Checking EU-Supply UK (uk.eu-supply.com)...")

    tenders = []
    base_url = "https://uk.eu-supply.com"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Referer": f"{base_url}/ctm/supplier/publictenders?B=UK",
    }

    session = requests.Session()

    for page in range(1, pages + 1):
        print(f"  Scraping EU-Supply UK page {page}...")

        # Confirmed pagination pattern from live HTML pager links:
        # Page 1: /ctm/supplier/publictenders?B=UK
        # Page 2: /ctm/supplier/2  (note: no ?B=UK needed, session cookie handles it)
        if page == 1:
            url = f"{base_url}/ctm/supplier/publictenders?B=UK"
        else:
            url = f"{base_url}/ctm/supplier/publictenders/{page}?B=UK"

        try:
            res = session.get(url, headers=headers, timeout=15)
            res.raise_for_status()
        except requests.RequestException as e:
            print(f"  EU-Supply UK page {page} error: {e}")
            break

        page_tenders = _parse_eusupply_table(res.text, base_url, keyword)

        if not page_tenders:
            print(f"  EU-Supply UK page {page}: no results, stopping.")
            break

        tenders.extend(page_tenders)
        print(f"  EU-Supply UK page {page}: {len(page_tenders)} tenders.")
        time.sleep(1)

    print(f"EU-Supply UK scraped total: {len(tenders)} tenders.")
    return tenders


def _parse_eusupply_table(html: str, base_url: str, keyword: str = "") -> list[dict]:
    """
    Parse the public tenders table from eu-supply.com.

    The table has a clear <thead> with column headers and <tbody> with data rows.
    Each title cell contains an <a> with the full tender URL.
    """
    soup = BeautifulSoup(html, "html.parser")
    tenders = []

    # Find the table — confirmed headers: "Quote/tender Id", "Reference", "Name"
    target_table = None
    for table in soup.find_all("table"):
        header_text = table.get_text(" ", strip=True)
        if "Quote/tender Id" in header_text and "Response deadline" in header_text:
            target_table = table
            break

    if not target_table:
        # Fallback: any table with 7+ columns
        for table in soup.find_all("table"):
            if len(table.find_all("th")) >= 7:
                target_table = table
                break

    if not target_table:
        return tenders

    rows = target_table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")

        # Need exactly 8 columns; skip header rows (<th> only)
        if len(cols) < 7:
            continue

        # ── Col 0: Tender ID ────────────────────────────────────────────
        tender_id = cols[0].get_text(strip=True)

        # ── Col 1: Reference ────────────────────────────────────────────
        reference = cols[1].get_text(strip=True)

        # ── Col 2: Name + link ──────────────────────────────────────────
        a_tag = cols[2].find("a")
        if not a_tag:
            continue

        title = a_tag.get_text(separator=" ", strip=True)
        if not title:
            continue

        href = a_tag.get("href", "")
        url = href if href.startswith("http") else (base_url + href if href else "")

        # ── Col 3: Date Published ───────────────────────────────────────
        date_published = cols[3].get_text(strip=True)  # dd/mm/yyyy

        # ── Col 4: Response Deadline ────────────────────────────────────
        deadline = cols[4].get_text(strip=True)  # dd/mm/yyyy HH:MM

        # ── Col 5: Procedure ────────────────────────────────────────────
        procedure = cols[5].get_text(separator=" ", strip=True)

        # ── Col 6: Buyer / Contracting Authority ────────────────────────
        buyer = cols[6].get_text(separator=" ", strip=True)

        # ── Col 7: Country (if present) ─────────────────────────────────
        country = cols[7].get_text(strip=True) if len(cols) > 7 else "United Kingdom"

        # ── Optional keyword filter ─────────────────────────────────────
        if keyword and keyword.lower() not in title.lower():
            continue

        tenders.append({
            "title": title,
            "description": f"{procedure} — {buyer}",   # enriches scorer
            "reference": reference,
            "tender_id": tender_id,
            "buyer": buyer,
            "organisation": buyer,                      # used by emailer
            "procedure": procedure,
            "date_published": date_published,
            "deadline": deadline,
            "country": country,
            "url": url,
            "source": "eusupply_uk",
        })

    return tenders

if __name__ == "__main__":
    results = scrape_eusupply_uk(pages=2)
    for r in results[:5]:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    print(f"\nTotal: {len(results)}")