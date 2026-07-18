"""Parse schema.org JSON-LD embedded in a page for Organization firmographics.

Many company sites ship a `<script type="application/ld+json">` block describing
themselves as an Organization: founding date, HQ address, logo, headcount, and
`sameAs` links to their social profiles. It's all free, structured data on a
page we've already downloaded. Everything here is best-effort and never raises.
"""
import json
import re

from bs4 import BeautifulSoup

_ORG_TYPES = {
    "organization", "corporation", "localbusiness", "onlinebusiness",
    "ngo", "educationalorganization", "governmentorganization",
    "nonprofit", "company",
}


def _iter_ldjson(html):
    """Yield every JSON object found in the page's ld+json scripts."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all("script", type="application/ld+json"):
        raw = tag.string or tag.get_text()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        yield from _flatten(data)


def _flatten(data):
    if isinstance(data, list):
        for item in data:
            yield from _flatten(item)
    elif isinstance(data, dict):
        if "@graph" in data:
            yield from _flatten(data["@graph"])
        else:
            yield data


def _is_org(node):
    t = node.get("@type")
    types = [t] if isinstance(t, str) else (t or [])
    return any(str(x).lower() in _ORG_TYPES for x in types)


def _year(value):
    if not value:
        return None
    m = re.search(r"\d{4}", str(value))
    return m.group(0) if m else None


def _address(node):
    addr = node.get("address")
    if isinstance(addr, list):
        addr = addr[0] if addr else None
    if isinstance(addr, str):
        return addr.strip() or None
    if isinstance(addr, dict):
        parts = [
            addr.get("addressLocality"),
            addr.get("addressRegion"),
            addr.get("addressCountry"),
        ]
        parts = [str(p).strip() for p in parts if p]
        return ", ".join(dict.fromkeys(parts)) or None
    return None


def _logo(node):
    logo = node.get("logo") or node.get("image")
    if isinstance(logo, list):
        logo = logo[0] if logo else None
    if isinstance(logo, dict):
        logo = logo.get("url")
    return logo if isinstance(logo, str) else None


def _employees(node):
    val = node.get("numberOfEmployees")
    if isinstance(val, dict):
        val = val.get("value") or val.get("minValue")
    return str(val).strip() if val else None


def _same_as(node):
    urls = node.get("sameAs")
    if isinstance(urls, str):
        return [urls]
    if isinstance(urls, list):
        return [u for u in urls if isinstance(u, str)]
    return []


def extract_org(html):
    """Return firmographic fields from JSON-LD (first non-empty value wins)."""
    result = {
        "founded": None,
        "hq_location": None,
        "employee_count": None,
        "logo": None,
        "same_as": [],
    }
    if not html:
        return result

    seen_same_as = set()
    for node in _iter_ldjson(html):
        if not isinstance(node, dict) or not _is_org(node):
            continue
        result["founded"] = result["founded"] or _year(node.get("foundingDate"))
        result["hq_location"] = result["hq_location"] or _address(node)
        result["employee_count"] = result["employee_count"] or _employees(node)
        result["logo"] = result["logo"] or _logo(node)
        for u in _same_as(node):
            if u not in seen_same_as:
                seen_same_as.add(u)
                result["same_as"].append(u)

    return result
