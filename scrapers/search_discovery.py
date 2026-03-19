import requests
from bs4 import BeautifulSoup


def search_duckduckgo(query):

    url = "https://html.duckduckgo.com/html/"

    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.post(url, data={"q": query}, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    links = []

    for a in soup.find_all("a", class_="result__a"):

        links.append(a["href"])

    return links