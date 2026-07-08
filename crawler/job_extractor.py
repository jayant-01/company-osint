"""Fetch structured job listings from detected ATS providers.

Each extractor receives the raw ATS link that was found on the page, parses the
company token/slug out of it, and calls the provider's public JSON API.
"""
import requests
from urllib.parse import urlparse, parse_qs, urljoin

from bs4 import BeautifulSoup

TIMEOUT = 15


def _first_path_segment(url, skip=()):
    parts = [p for p in urlparse(url).path.split("/") if p and p not in skip]
    return parts[0] if parts else None


# ---------------------------
# GREENHOUSE
# https://boards-api.greenhouse.io/v1/boards/{token}/jobs
# ---------------------------
def _greenhouse_token(url):
    qs = parse_qs(urlparse(url).query)
    if qs.get("for"):
        return qs["for"][0]
    return _first_path_segment(
        url, skip=("embed", "job_board", "js", "css", "v1", "boards")
    )


def extract_greenhouse(url):
    token = _greenhouse_token(url)
    if not token:
        return []
    api = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    try:
        data = requests.get(api, timeout=TIMEOUT).json()
        return [
            {
                "title": job.get("title"),
                "location": (job.get("location") or {}).get("name"),
                "url": job.get("absolute_url"),
            }
            for job in data.get("jobs", [])
        ]
    except Exception:
        return []


# ---------------------------
# LEVER
# https://api.lever.co/v0/postings/{token}?mode=json
# ---------------------------
def _lever_token(url):
    return _first_path_segment(url, skip=("v0", "postings"))


def extract_lever(url):
    token = _lever_token(url)
    if not token:
        return []
    api = f"https://api.lever.co/v0/postings/{token}?mode=json"
    try:
        data = requests.get(api, timeout=TIMEOUT).json()
        return [
            {
                "title": job.get("text"),
                "location": (job.get("categories") or {}).get("location"),
                "url": job.get("hostedUrl"),
            }
            for job in data
        ]
    except Exception:
        return []


# ---------------------------
# ASHBY
# https://api.ashbyhq.com/posting-api/job-board/{token}
# ---------------------------
def _ashby_token(url):
    host = urlparse(url).netloc.lower()
    if host.endswith("ashbyhq.com"):
        sub = host[: -len("ashbyhq.com")].strip(".")
        if sub and sub not in ("jobs", "api", "www"):
            return sub
    return _first_path_segment(url, skip=("posting-api", "job-board"))


def extract_ashby(url):
    token = _ashby_token(url)
    if not token:
        return []
    api = f"https://api.ashbyhq.com/posting-api/job-board/{token}"
    try:
        data = requests.get(api, timeout=TIMEOUT).json()
        return [
            {
                "title": job.get("title"),
                "location": job.get("location"),
                "url": job.get("jobUrl") or job.get("applyUrl"),
            }
            for job in data.get("jobs", [])
        ]
    except Exception:
        return []


# ---------------------------
# GENERIC FALLBACK (scrape anchor text on a page)
# ---------------------------
def extract_generic(html, base_url):
    soup = BeautifulSoup(html, "lxml")
    keywords = ("engineer", "developer", "intern", "manager", "analyst")
    jobs = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        if text and any(k in text.lower() for k in keywords):
            jobs.append({
                "title": text,
                "location": None,
                "url": urljoin(base_url, a["href"]),
            })
    return jobs
