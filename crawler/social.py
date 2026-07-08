"""Extract social / developer profile links from a list of page links."""
from urllib.parse import urlparse

SOCIAL_HOSTS = {
    "github": ("github.com",),
    "linkedin": ("linkedin.com",),
    "twitter": ("twitter.com", "x.com"),
    "facebook": ("facebook.com",),
    "instagram": ("instagram.com",),
    "youtube": ("youtube.com", "youtu.be"),
}


def extract_socials(links):
    """Return the first matching URL for each known social platform."""
    found = {}
    for link in links:
        host = urlparse(link).netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        if not host:
            continue
        for name, hosts in SOCIAL_HOSTS.items():
            if name in found:
                continue
            if any(host == h or host.endswith("." + h) for h in hosts):
                found[name] = link
    return found
