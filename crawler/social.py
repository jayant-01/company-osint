"""Extract social / developer / professional profile links from page links."""
from urllib.parse import urlparse

SOCIAL_HOSTS = {
    "github": ("github.com",),
    "linkedin": ("linkedin.com",),
    "twitter": ("twitter.com", "x.com"),
    "facebook": ("facebook.com", "fb.com"),
    "instagram": ("instagram.com",),
    "youtube": ("youtube.com", "youtu.be"),
    "crunchbase": ("crunchbase.com",),
    "wellfound": ("wellfound.com", "angel.co"),
    "medium": ("medium.com",),
    "devto": ("dev.to",),
    "gitlab": ("gitlab.com",),
    "discord": ("discord.gg", "discord.com"),
    "telegram": ("t.me", "telegram.me"),
    "bluesky": ("bsky.app",),
    "stackoverflow": ("stackoverflow.com",),
    "producthunt": ("producthunt.com",),
    "tiktok": ("tiktok.com",),
}


def _host(url):
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def classify_social(url):
    """Return the platform name for a URL, or None if it isn't a known one."""
    host = _host(url)
    if not host:
        return None
    for name, hosts in SOCIAL_HOSTS.items():
        if any(host == h or host.endswith("." + h) for h in hosts):
            return name
    return None


def extract_socials(links):
    """Return the first matching URL for each known platform, in link order."""
    found = {}
    for link in links:
        name = classify_social(link)
        if name and name not in found:
            found[name] = link
    return found


def merge_social_urls(socials, urls):
    """Fill gaps in `socials` from a list of URLs (e.g. JSON-LD sameAs)."""
    for url in urls:
        name = classify_social(url)
        if name and name not in socials:
            socials[name] = url
    return socials
