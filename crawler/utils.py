from urllib.parse import urljoin

import tldextract

# Use the snapshot bundled with tldextract (no network call for the public
# suffix list, and no disk cache writes) so domain parsing works offline.
_extract = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None)


def absolute(base, href):
    return urljoin(base, href)


def registered_domain(url):
    """e.g. 'https://careers.stripe.com/x' -> 'stripe.com'."""
    ext = _extract(url)
    if ext.suffix:
        return f"{ext.domain}.{ext.suffix}".lower()
    return (ext.domain or "").lower()


def domain_core(url):
    """The core label of the domain, e.g. 'stripe.com' -> 'stripe'."""
    return (_extract(url).domain or "").lower()
