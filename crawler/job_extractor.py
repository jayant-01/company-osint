"""Fetch structured job listings from detected ATS providers."""
import requests
from urllib.parse import urljoin

from bs4 import BeautifulSoup


# ---------------------------
# GREENHOUSE
# ---------------------------
def extract_greenhouse(url):

    try:

        # boards.greenhouse.io/company OR API endpoint
        if not url.endswith(".json"):

            url = url + ("?format=json" if url.endswith("/") else ".json")

        r = requests.get(url, timeout=15)

        data = r.json()

        jobs = []

        for dept in data:

            for job in dept.get("jobs", []):

                jobs.append({
                    "title": job.get("title"),
                    "location": (job.get("location") or {}).get("name"),
                    "url": job.get("absolute_url"),
                })

        return jobs

    except Exception:

        return []


# ---------------------------
# LEVER
# ---------------------------
def extract_lever(url):

    try:

        if not url.endswith("/postings"):

            url = url + ("postings" if url.endswith("/") else "/postings")

        r = requests.get(url, timeout=15)

        data = r.json()

        jobs = []

        for job in data:

            jobs.append({
                "title": job.get("text"),
                "location": (job.get("categories") or {}).get("location"),
                "url": job.get("hostedUrl"),
            })

        return jobs

    except Exception:

        return []


# ---------------------------
# GENERIC FALLBACK
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
