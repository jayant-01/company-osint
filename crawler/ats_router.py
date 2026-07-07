from crawler.job_extractor import (
    extract_greenhouse,
    extract_lever,
    extract_generic
)


def extract_jobs(ats_list, html=None):

    all_jobs = []

    for ats in ats_list:

        provider = ats["provider"]
        url = ats["url"]

        if provider == "greenhouse":

            all_jobs.extend(extract_greenhouse(url))

        elif provider == "lever":

            all_jobs.extend(extract_lever(url))

        else:

            # fallback later
            pass

    return all_jobs