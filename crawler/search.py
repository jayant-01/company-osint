import re

try:
    # Package was renamed from `duckduckgo_search` to `ddgs`.
    from ddgs import DDGS
except ImportError:  # pragma: no cover - fallback for older installs
    from duckduckgo_search import DDGS

from urllib.parse import urlparse
from rapidfuzz import fuzz

from crawler.constants import BLACKLIST_DOMAINS
from crawler.utils import domain_core


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


def _norm(text):
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def rank_websites(company, websites):
    """Rank candidate URLs by how well the domain matches the company name.

    Fuzzy score is primary; the original search order breaks ties.
    """
    target = _norm(company)
    scored = []
    for i, url in enumerate(websites):
        core = _norm(domain_core(url))
        score = max(fuzz.ratio(target, core), fuzz.partial_ratio(target, core))
        # higher score first; earlier search result wins ties
        scored.append((score, -i, url))
    scored.sort(reverse=True)
    return [url for _, _, url in scored]


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
    return rank_websites(company, clean_results(results))
