import requests
from bs4 import BeautifulSoup
import time
import json


def scrape_etenders_ireland(pages: int = 3, keyword: str = "") -> list[dict]:
    """
    Scrape active Calls for Tender (CfTs) from Ireland's eTenders portal.
    Source: https://www.etenders.gov.ie

    Confirmed table structure (from live HTML):
        Col 0: # (row number)
        Col 1: Title (with <a> link) + description in img title attribute
        Col 2: Resource ID
        Col 3: Contracting Authority (CA)
        Col 4: Info icon (description text in title attr)
        Col 5: Date Published
        Col 6: Submission Deadline
        Col 7: Procedure
        Col 8: Status
        Col 9: Notice PDF (optional)
        Col 10: Award Date
        Col 11: Estimated Value
        Col 12: Cycle

    Pagination: GET param d-3680175-p=N (10 results per page, 2900+ total)

    Args:
        pages:   Number of pages to scrape (10 tenders/page).
        keyword: Optional case-insensitive title/description filter.

    Returns:
        List of dicts: title, description, contracting_authority,
                       date_published, deadline, procedure, status,
                       estimated_value, url, source
    """
    print("Checking eTenders Ireland (etenders.gov.ie)...")

    tenders = []
    base_url = "https://www.etenders.gov.ie"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-IE,en;q=0.9",
        "Referer": f"{base_url}/epps/home.do",
    }

    session = requests.Session()

    # Warm up: visit homepage to pick up session cookies
    try:
        session.get(f"{base_url}/epps/home.do", headers=headers, timeout=15)
        time.sleep(0.5)
    except Exception as e:
        print(f"  eTenders IE: warm-up failed: {e}")

    for page in range(1, pages + 1):
        print(f"  Scraping eTenders IE page {page}...")

        # Pagination param confirmed from sort links in live HTML
        url = (
            f"{base_url}/epps/quickSearchAction.do"
            f"?latest=true&searchType=cftFTS"
            f"&d-3680175-p={page}"
        )

        try:
            res = session.get(url, headers=headers, timeout=15)
            res.raise_for_status()
        except requests.RequestException as e:
            print(f"  eTenders IE page {page} error: {e}")
            break

        page_tenders = _parse_etenders_table(res.text, base_url, keyword)

        if not page_tenders:
            print(f"  eTenders IE page {page}: no results, stopping.")
            break

        tenders.extend(page_tenders)
        print(f"  eTenders IE page {page}: {len(page_tenders)} tenders.")
        time.sleep(1)

    print(f"eTenders IE scraped total: {len(tenders)} tenders.")
    return tenders


def _parse_etenders_table(html: str, base_url: str, keyword: str = "") -> list[dict]:
    """
    Parse the CfT results table from eTenders Ireland.

    The description is not in the table cells — it's hidden in the
    title attribute of the info icon <img> in col 4. We extract it
    from there since it contains the full tender description text.
    """
    soup = BeautifulSoup(html, "html.parser")
    tenders = []

    # Find the results table — it contains "Resource ID" and "Procedure" headers
    target_table = None
    for table in soup.find_all("table"):
        headers_text = table.get_text(" ", strip=True)
        if "Resource ID" in headers_text and "Procedure" in headers_text:
            target_table = table
            break

    if not target_table:
        return tenders

    rows = target_table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")

        # Need at least 8 columns (skip header/footer <th> rows)
        if len(cols) < 8:
            continue

        # ── Col 1: Title + link ─────────────────────────────────────────
        a_tag = cols[1].find("a")
        if not a_tag:
            continue

        title = a_tag.get_text(separator=" ", strip=True)
        if not title:
            continue

        href = a_tag.get("href", "")
        url = href if href.startswith("http") else (base_url + href if href else "")

        # ── Col 4: Description from info icon title attr ────────────────
        # The <img class="icon_information"> has the description in its
        # title attribute — this is the full tender description text
        description = ""
        info_img = cols[4].find("img") if len(cols) > 4 else None
        if info_img:
            description = info_img.get("title", "").strip()
        # Fallback: use the link title attr
        if not description:
            description = a_tag.get("title", "").strip()

        # ── Col 2: Resource ID ──────────────────────────────────────────
        resource_id = cols[2].get_text(strip=True)

        # ── Col 3: Contracting Authority ────────────────────────────────
        contracting_authority = cols[3].get_text(separator=" ", strip=True)

        # ── Col 5: Date Published ───────────────────────────────────────
        date_published = _clean_date(cols[5].get_text(strip=True))

        # ── Col 6: Submission Deadline ──────────────────────────────────
        deadline = _clean_date(cols[6].get_text(strip=True))

        # ── Col 7: Procedure ────────────────────────────────────────────
        procedure = cols[7].get_text(separator=" ", strip=True)

        # ── Col 8: Status ───────────────────────────────────────────────
        status = cols[8].get_text(separator=" ", strip=True) if len(cols) > 8 else ""

        # ── Col 11: Estimated Value ─────────────────────────────────────
        estimated_value = cols[11].get_text(strip=True) if len(cols) > 11 else ""

        # ── Optional keyword filter ─────────────────────────────────────
        searchable = f"{title} {description}".lower()
        if keyword and keyword.lower() not in searchable:
            continue

        tenders.append({
            "title": title,
            "description": description,
            "resource_id": resource_id,
            "contracting_authority": contracting_authority,
            "date_published": date_published,
            "deadline": deadline,
            "procedure": procedure,
            "status": status,
            "estimated_value": estimated_value,
            "url": url,
            "source": "etenders_ie",
        })

    return tenders


def _clean_date(raw: str) -> str:
    """
    Convert eTenders date format to a clean string.
    Input:  'Wed Jun 03 09:37:27 IST 2026'
    Output: '03 Jun 2026 09:37'
    """
    try:
        parts = raw.split()
        # Format: DayOfWeek Month DayNum Time TZ Year
        if len(parts) >= 6:
            return f"{parts[2]} {parts[1]} {parts[5]} {parts[3][:5]}"
    except Exception:
        pass
    return raw.strip()


# ── Wire into main.py ───────────────────────────────────────────────────────
# In SCRAPERS dict add:
#   "etenders_ie": scrape_etenders_ireland,
#
# In THRESHOLDS add:
#   "etenders_ie": {"high": 0.36, "low": 0.25},
#
# In is_relevant() trusted keyword sources add "etenders_ie":
#   if kw_match and source in ("uk", "findatender", "ted", "samgov", "gem", "etenders_ie"):


if __name__ == "__main__":
    results = scrape_etenders_ireland(pages=2)
    for r in results[:5]:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    print(f"\nTotal: {len(results)}")