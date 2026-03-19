import requests
from bs4 import BeautifulSoup
import time


def scrape_generic(url):

    try:

        time.sleep(1)

        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.string if soup.title else url

        text = soup.get_text(" ", strip=True)

        return {

            "title": title[:200],
            "description": text[:2000],
            "link": url,
            "source": "Generic"

        }

    except:

        return None