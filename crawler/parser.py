from bs4 import BeautifulSoup


def extract_metadata(html):
    soup = BeautifulSoup(html, "lxml")
    title = ""
    if soup.title:
        title = soup.title.text.strip()
    description = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        description = meta.get("content", "")
    h1 = ""
    h = soup.find("h1")
    if h:
        h1 = h.text.strip()
    return {
        "title": title,
        "description": description,
        "h1": h1,
    }