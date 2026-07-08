"""Route detected ATS providers to the right job extractor, then de-duplicate."""
from crawler.job_extractor import (
    extract_greenhouse,
    extract_lever,
    extract_ashby,
)

EXTRACTORS = {
    "greenhouse": extract_greenhouse,
    "lever": extract_lever,
    "ashby": extract_ashby,
}


def extract_jobs(ats_list, html=None):

    all_jobs = []
    seen_calls = set()

    for ats in ats_list:

        provider = ats.get("provider")
        url = ats.get("url")

        extractor = EXTRACTORS.get(provider)
        if not extractor:
            continue

        key = (provider, url)
        if key in seen_calls:
            continue
        seen_calls.add(key)

        all_jobs.extend(extractor(url))

    # de-duplicate jobs by URL (falling back to title)
    unique = []
    seen_jobs = set()
    for job in all_jobs:
        ident = job.get("url") or job.get("title")
        if not ident or ident in seen_jobs:
            continue
        seen_jobs.add(ident)
        unique.append(job)

    return unique
