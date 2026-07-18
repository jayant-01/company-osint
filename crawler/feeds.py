"""Discover RSS / Atom / JSON feed URLs declared in a page's <head>.

Reads the `<link rel="alternate" type="application/rss+xml">` tags a site
publishes for feed readers — a clean, zero-extra-request way to find a blog's
feed for later monitoring.
"""
from urllib.parse import urljoin

from bs4 import BeautifulSoup

_FEED_TYPES = (
    "application/rss+xml",
    "application/atom+xml",
    "application/feed+json",
    "application/json",
)


def extract_feeds(base_url, html):
    """Return absolute feed URLs declared via <link rel="alternate">."""
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")
    feeds, seen = [], set()
    for link in soup.find_all("link", rel=True):
        rels = link.get("rel") or []
        if isinstance(rels, str):
            rels = [rels]
        if "alternate" not in [r.lower() for r in rels]:
            continue
        if (link.get("type") or "").lower() not in _FEED_TYPES:
            continue
        href = (link.get("href") or "").strip()
        if not href:
            continue
        url = urljoin(base_url, href)
        if url not in seen:
            seen.add(url)
            feeds.append(url)
    return feeds
