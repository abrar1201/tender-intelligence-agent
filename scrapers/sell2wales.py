import requests
from bs4 import BeautifulSoup
import time
import json


def scrape_sell2wales(pages: int = 5, keyword: str = "") -> list[dict]:
    """
    Scrape active tender notices from Sell2Wales (Welsh Government procurement portal).
    Source: https://www.sell2wales.gov.wales/Search/Search_MainPage.aspx

    Confirmed structure (from live HTML — card-based layout, 10 results/page):
        - Title: <a> inside each result card
        - Description: paragraph text below title (truncated snippet)
        - Reference No, OCID, Published By, Publication Date, Deadline, Value
        - Pagination: ?page=N  (2,439 results = 244 pages)
        - Notice types filtered to "Current Opportunity" only

    Args:
        pages:   Number of pages (10 tenders/page, default 5 = 50 tenders).
        keyword: Optional case-insensitive title/description filter.

    Returns:
        List of dicts: title, description, reference_no, buyer,
                       date_published, deadline, value, location, url, source
    """
    print("Checking Sell2Wales (sell2wales.gov.wales)...")

    tenders = []
    base_url = "https://www.sell2wales.gov.wales"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Referer": f"{base_url}/Search/Search_MainPage.aspx",
    }

    session = requests.Session()

    # Warm up — picks up session cookie
    try:
        session.get(f"{base_url}/Search/Search_MainPage.aspx", headers=headers, timeout=15)
        time.sleep(0.5)
    except Exception as e:
        print(f"  Sell2Wales: warm-up failed: {e}")

    for page in range(1, pages + 1):
        print(f"  Scraping Sell2Wales page {page}...")

        # Filter to Current Opportunity only — avoids awarded/pipeline noise
        url = (
            f"{base_url}/Search/Search_MainPage.aspx"
            f"?NoticeType=2"          # 2 = Current Opportunity
            f"&SortBy=3"              # 3 = Latest Publication Date
            f"&page={page}"
        )

        try:
            res = session.get(url, headers=headers, timeout=15)
            res.raise_for_status()
        except requests.RequestException as e:
            print(f"  Sell2Wales page {page} error: {e}")
            break

        page_tenders = _parse_sell2wales_cards(res.text, base_url, keyword)

        if not page_tenders:
            print(f"  Sell2Wales page {page}: no results, stopping.")
            break

        tenders.extend(page_tenders)
        print(f"  Sell2Wales page {page}: {len(page_tenders)} tenders.")
        time.sleep(1)

    print(f"Sell2Wales scraped total: {len(tenders)} tenders.")
    return tenders


def _parse_sell2wales_cards(html: str, base_url: str, keyword: str = "") -> list[dict]:
    """
    Parse the card-based tender listing from Sell2Wales search results.

    Each result is a <div> or <article> block containing:
        <a href="/search/show/search_view.aspx?ID=...">Title</a>
        <p>Description snippet</p>
        Reference no: XXX
        Published by: Organisation Name
        Publication date: DD/MM/YYYY
        Deadline date: DD/MM/YYYY
        Value: (number or -)
        Location: WALES / region
    """
    soup = BeautifulSoup(html, "html.parser")
    tenders = []

    # Each result card contains a link to /search/show/search_view.aspx
    # Find all such anchor tags — they are the title links
    result_links = soup.find_all(
        "a", href=lambda h: h and "search_view.aspx" in h.lower()
    )

    for a_tag in result_links:
        title = a_tag.get_text(separator=" ", strip=True)
        if not title:
            continue

        href = a_tag.get("href", "")
        url = href if href.startswith("http") else (base_url + href if href else "")

        # The card container is the closest ancestor div/article/li
        # Walk up to find the block that holds all the metadata
        card = a_tag.find_parent("div") or a_tag.find_parent("li") or a_tag.find_parent("article")
        if not card:
            continue

        card_text = card.get_text(separator="\n", strip=True)
        lines = [l.strip() for l in card_text.splitlines() if l.strip()]

        # ── Description: first substantial paragraph after title ─────────
        description = ""
        for line in lines:
            if line == title:
                continue
            # Skip metadata label lines like "Reference no:", "Published by:"
            if any(line.startswith(label) for label in [
                "Reference no:", "OCID:", "Published by:", "Publication date:",
                "Deadline date:", "Notice Type:", "Location:", "Value:"
            ]):
                break
            if len(line) > 30:
                description = line
                break

        # ── Extract labelled metadata fields ────────────────────────────
        reference_no  = _extract_field(card_text, "Reference no:")
        buyer         = _extract_field(card_text, "Published by:")
        date_pub      = _extract_field(card_text, "Publication date:")
        deadline      = _extract_field(card_text, "Deadline date:")
        value         = _extract_field(card_text, "Value:")
        location      = _extract_field(card_text, "Location:")
        notice_type   = _extract_field(card_text, "Notice Type:")

        # ── Optional keyword filter ─────────────────────────────────────
        searchable = f"{title} {description}".lower()
        if keyword and keyword.lower() not in searchable:
            continue

        tenders.append({
            "title": title,
            "description": description,
            "reference_no": reference_no,
            "buyer": buyer,
            "organisation": buyer,          # used by emailer
            "date_published": date_pub,
            "deadline": deadline,
            "value": value,
            "location": location,
            "notice_type": notice_type,
            "url": url,
            "source": "sell2wales",
        })

    return tenders


def _extract_field(text: str, label: str) -> str:
    """
    Extract the value after a label like 'Reference no: APR607576'.
    Handles multi-line card text by finding the label then grabbing
    the next non-empty token on the same line or the next line.
    """
    idx = text.find(label)
    if idx == -1:
        return ""
    after = text[idx + len(label):]
    # Get everything up to next newline
    line = after.split("\n")[0].strip()
    # If empty, try next line
    if not line:
        lines = after.split("\n")
        for l in lines[1:]:
            if l.strip():
                line = l.strip()
                break
    return line


if __name__ == "__main__":
    results = scrape_sell2wales(pages=2)
    for r in results[:5]:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    print(f"\nTotal: {len(results)}")