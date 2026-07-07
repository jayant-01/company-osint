from duckduckgo_search import DDGS
from urllib.parse import urlparse
from crawler.constants import BLACKLIST_DOMAINS


def clean_results(results):
    websites = []
    for r in results:
        href = r.get("href")
        if not href:
            continue
        domain = urlparse(href).netloc.lower()
        domain = domain.replace("www.", "")
        if any(x in domain for x in BLACKLIST_DOMAINS):
            continue
        websites.append(href)
    return websites


def search_company(company):
    with DDGS() as ddgs:
        results = list(
            ddgs.text(
                f"{company} official website",
                max_results=10,
            )
        )
    return clean_results(results)