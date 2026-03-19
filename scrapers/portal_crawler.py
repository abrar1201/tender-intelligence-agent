from portal_db import get_portals
from scrapers.generic import scrape_generic


def crawl_portals():

    tenders = []

    portals = get_portals()

    for domain in portals:

        url = f"https://{domain}"

        result = scrape_generic(url)

        if result:

            tenders.append(result)

    return tenders