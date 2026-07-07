from urllib.parse import urljoin


def absolute(base, href):
    return urljoin(base, href)