from bs4 import BeautifulSoup
from urllib.parse import urljoin


def extract_links(base_url, html):
    soup = BeautifulSoup(html, "lxml")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        full_url = urljoin(base_url, href)
        links.add(full_url)
    return list(links)