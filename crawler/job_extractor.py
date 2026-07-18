"""Fetch structured job listings from detected ATS providers.

Each extractor receives the raw ATS link that was found on the page, parses the
company token/slug out of it, and calls the provider's public JSON API. Beyond
title/location/url we also pull department, employment type, a remote flag and
the posted date — all already present in the same JSON response.
"""
from datetime import datetime, timezone

import requests
from urllib.parse import urlparse, parse_qs, urljoin

from bs4 import BeautifulSoup

TIMEOUT = 15


def _first_path_segment(url, skip=()):
    parts = [p for p in urlparse(url).path.split("/") if p and p not in skip]
    return parts[0] if parts else None


def _iso_date(value):
    """Return the YYYY-MM-DD portion of an ISO-8601 timestamp, if present."""
    if not value or not isinstance(value, str):
        return None
    m = value[:10]
    return m if len(m) == 10 and m[4] == "-" and m[7] == "-" else None


def _epoch_ms_date(value):
    """Convert a millisecond epoch (int or numeric str) to YYYY-MM-DD."""
    try:
        ts = int(value) / 1000
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
    except (TypeError, ValueError, OSError):
        return None


def _remote_from_location(location):
    return "remote" if location and "remote" in location.lower() else None


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


def _greenhouse_department(job):
    depts = job.get("departments") or []
    for d in depts:
        name = (d or {}).get("name")
        if name:
            return name
    return None


def extract_greenhouse(url):
    token = _greenhouse_token(url)
    if not token:
        return []
    api = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    try:
        data = requests.get(api, timeout=TIMEOUT).json()
        jobs = []
        for job in data.get("jobs", []):
            location = (job.get("location") or {}).get("name")
            jobs.append({
                "title": job.get("title"),
                "location": location,
                "url": job.get("absolute_url"),
                "department": _greenhouse_department(job),
                "employment_type": None,
                "remote": _remote_from_location(location),
                "posted": _iso_date(job.get("updated_at")),
            })
        return jobs
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
        jobs = []
        for job in data:
            cats = job.get("categories") or {}
            location = cats.get("location")
            workplace = job.get("workplaceType")
            jobs.append({
                "title": job.get("text"),
                "location": location,
                "url": job.get("hostedUrl"),
                "department": cats.get("team") or cats.get("department"),
                "employment_type": cats.get("commitment"),
                "remote": (workplace.lower() if workplace else None)
                or _remote_from_location(location),
                "posted": _epoch_ms_date(job.get("createdAt")),
            })
        return jobs
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
        jobs = []
        for job in data.get("jobs", []):
            location = job.get("location")
            remote = "remote" if job.get("isRemote") else _remote_from_location(location)
            jobs.append({
                "title": job.get("title"),
                "location": location,
                "url": job.get("jobUrl") or job.get("applyUrl"),
                "department": job.get("department") or job.get("team"),
                "employment_type": job.get("employmentType"),
                "remote": remote,
                "posted": _iso_date(job.get("publishedAt")),
            })
        return jobs
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
                "department": None,
                "employment_type": None,
                "remote": None,
                "posted": None,
            })
    return jobs
