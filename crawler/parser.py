from bs4 import BeautifulSoup


def _meta_content(soup, **attrs):
    tag = soup.find("meta", attrs=attrs)
    return (tag.get("content") or "").strip() if tag else ""


def extract_metadata(html):
    soup = BeautifulSoup(html, "lxml")

    title = ""
    if soup.title:
        title = soup.title.text.strip()
    title = title or _meta_content(soup, property="og:title")

    # Prefer the standard meta description, fall back to og:description, then h1.
    description = _meta_content(soup, name="description")
    description = description or _meta_content(soup, property="og:description")

    h1 = ""
    h = soup.find("h1")
    if h:
        h1 = h.text.strip()
    description = description or h1

    return {
        "title": title,
        "description": description,
        "h1": h1,
    }