import requests
import json
from ai.hf_client import classify_job
from ai.scoring import score_job

# ---------------------------
# GREENHOUSE
# ---------------------------
def extract_greenhouse(url):

    try:

        # boards.greenhouse.io/company OR API endpoint
        if not url.endswith(".json"):

            if url.endswith("/"):

                url = url + "?format=json"

            else:

                url = url + ".json"

        r = requests.get(url, timeout=15)

        data = r.json()

        jobs = []

        for dept in data:

            for job in dept.get("jobs", []):

                jobs.append({
                    "title": job.get("title"),
                    "location": job.get("location", {}).get("name"),
                    "url": job.get("absolute_url")
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

            if url.endswith("/"):

                url = url + "postings"

            else:

                url = url + "/postings"

        r = requests.get(url, timeout=15)

        data = r.json()

        jobs = []

        for job in data:

            jobs.append({
                "title": job.get("text"),
                "location": job.get("categories", {}).get("location"),
                "url": job.get("hostedUrl")
            })

        return jobs

    except Exception:

        return []


# ---------------------------
# GENERIC FALLBACK
# ---------------------------
def extract_generic(html, base_url):

    from bs4 import BeautifulSoup
    from urllib.parse import urljoin

    soup = BeautifulSoup(html, "lxml")

    jobs = []

    for a in soup.find_all("a", href=True):

        text = a.text.lower()

        if any(k in text for k in ["engineer", "developer", "intern", "manager", "analyst"]):

            jobs.append({
                "title": a.text.strip(),
                "url": urljoin(base_url, a["href"])
            })

    return jobs

def enrich_jobs(jobs, user_profile):

    enriched = []

    for job in jobs:

        text = job.get("title", "") + " " + job.get("description", "")

        classification = classify_job(text)

        relevance = score_job(text, user_profile)

        job["role_type"] = classification["label"]

        job["role_confidence"] = classification["score"]

        job["match_score"] = relevance

        enriched.append(job)

    return enriched