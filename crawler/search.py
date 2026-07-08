try:
    # Package was renamed from `duckduckgo_search` to `ddgs`.
    from ddgs import DDGS
except ImportError:  # pragma: no cover - fallback for older installs
    from duckduckgo_search import DDGS

from urllib.parse import urlparse
from crawler.constants import BLACKLIST_DOMAINS


def clean_results(results):
    websites = []
    for r in results:
        href = r.get("href") or r.get("url")
        if not href:
            continue
        domain = urlparse(href).netloc.lower().replace("www.", "")
        if any(x in domain for x in BLACKLIST_DOMAINS):
            continue
        websites.append(href)
    return websites


def search_company(company):
    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.text(
                    f"{company} official website",
                    max_results=10,
                )
            )
    except Exception:
        # Rate limits / network errors should not crash the whole run.
        return []
    return clean_results(results)
