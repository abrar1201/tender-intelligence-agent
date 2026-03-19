from urllib.parse import urlparse
from scrapers.generic import scrape_generic
from ai.portal_classifier import is_procurement_portal
from portal_db import save_portal


def discover_portals(links):

    portals = []

    for link in links:

        result = scrape_generic(link)

        if not result:
            continue

        text = result["description"]

        if is_procurement_portal(text):

            domain = urlparse(link).netloc

            save_portal(domain)

            portals.append(domain)

    return portals