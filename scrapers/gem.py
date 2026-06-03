import requests
from bs4 import BeautifulSoup
import time
import json


def scrape_gem(pages: int = 3, keyword: str = "") -> list[dict]:
    """
    Scrape active tenders from CPPP / eProcure (India's national procurement portal).
    Source: https://eprocure.gov.in/eprocure/app

    The homepage shows two tables: Latest Tenders + Latest Corrigendums.
    We scrape ONLY the Latest Tenders table (not corrigendums, not nav links).
    Each row: Col0=Title+Link | Col1=Reference No | Col2=Closing Date | Col3=Opening Date
    """
    print("Checking GeM/CPPP (eprocure.gov.in)...")

    base_url = "https://eprocure.gov.in"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-IN,en;q=0.9",
        "Referer": f"{base_url}/eprocure/app",
    }

    session = requests.Session()
    tenders = []

    for page in range(1, pages + 1):
        print(f"  Scraping GeM/CPPP page {page}...")
        # The homepage paginates via this GET param
        url = f"{base_url}/eprocure/app?page=FrontEndListTendersbyDate&service=page&pageIndex={page}"
        # Page 1: use the homepage directly (always accessible)
        if page == 1:
            url = f"{base_url}/eprocure/app"

        try:
            res = session.get(url, headers=headers, timeout=15)
            res.raise_for_status()
        except requests.RequestException as e:
            print(f"  GeM/CPPP page {page} error: {e}")
            break

        page_tenders = _parse_homepage_tenders_only(res.text, base_url, keyword)

        if not page_tenders:
            print(f"  GeM/CPPP page {page}: no tenders found, stopping.")
            break

        tenders.extend(page_tenders)
        print(f"  GeM/CPPP page {page}: {len(page_tenders)} tenders.")
        time.sleep(1)

    print(f"GeM scraped total: {len(tenders)} tenders.")
    return tenders


def _parse_homepage_tenders_only(html: str, base_url: str, keyword: str = "") -> list[dict]:
    """
    Parse ONLY the 'Latest Tenders' table from the eprocure homepage.

    Strategy: The homepage has this exact structure:
        <li>Latest Tenders</li>          ← section heading
        <li>Tender Title | Reference No | Closing Date | Bid Opening Date</li>  ← column headers
        <li>row 1 ... row 10</li>        ← tender rows
        <li>Latest Tenders updates every 15 mins. More...</li>
        <li>Latest Corrigendums</li>     ← STOP here, don't read corrigendums

    We find the table that has BOTH "Tender Title" AND "Reference No" headers,
    and stop parsing when we hit corrigendum rows.
    """
    soup = BeautifulSoup(html, "html.parser")
    tenders = []

    # ── Find the correct table ──────────────────────────────────────────
    # The tenders table header row contains "Tender Title" and "Reference No"
    # The corrigendum table header contains "Corrigendum Title"
    # We want ONLY the first one.
    tender_table = None
    for table in soup.find_all("table"):
        text = table.get_text(" ", strip=True)
        if "Tender Title" in text and "Reference No" in text and "Corrigendum" not in text[:50]:
            tender_table = table
            break

    if not tender_table:
        return tenders

    rows = tender_table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")

        # Need 4 columns (S.No+Title | Ref No | Closing Date | Opening Date)
        if len(cols) != 4:
            continue

        # ── Col 0: Title + Link ─────────────────────────────────────────
        a_tag = cols[0].find("a")
        if not a_tag:
            continue

        title = a_tag.get_text(separator=" ", strip=True)

        # ── Hard filters — skip non-tender rows ─────────────────────────
        if not title:
            continue

        # Skip navigation links scraped accidentally
        NAV_TITLES = {
            "screen reader access", "search", "active tenders",
            "tenders by closing date", "corrigendum", "bid awards",
            "cppp home", "home", "contact us", "sitemap",
            "mis reports", "tenders by location", "tenders by organisation",
            "tenders by classification", "tenders in archive",
            "tenders status", "cancelled/retendered", "downloads",
            "debarment list", "announcements", "recognitions",
            "site compatibility", "national informatics centre",
            "more...", "back",
        }
        if title.lower().strip() in NAV_TITLES:
            continue

        # Skip corrigendum rows (they appear in a second table but just in case)
        title_lower = title.lower()
        if any(w in title_lower for w in ["corrigendum", "clarification", "pre-bid meeting",
                                           "bid submission duration", "date extension"]):
            continue

        # ── Col 1: Reference No ─────────────────────────────────────────
        reference_no = cols[1].get_text(separator=" ", strip=True)

        # ── Col 2: Closing Date ─────────────────────────────────────────
        closing_date = cols[2].get_text(separator=" ", strip=True)

        # ── Col 3: Bid Opening Date ─────────────────────────────────────
        opening_date = cols[3].get_text(separator=" ", strip=True)

        # ── Build URL ───────────────────────────────────────────────────
        href = a_tag.get("href", "")
        url = href if href.startswith("http") else (base_url + href if href else "")

        # ── Optional keyword filter ─────────────────────────────────────
        if keyword and keyword.lower() not in title_lower:
            continue

        tenders.append({
            "title": title,
            "description": f"{reference_no} {closing_date}",  # helps scorer
            "reference_no": reference_no,
            "closing_date": closing_date,
            "opening_date": opening_date,
            "url": url,
            "source": "gem",
        })

    return tenders


if __name__ == "__main__":
    results = scrape_gem(pages=1)
    for r in results:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    print(f"\nTotal: {len(results)}")