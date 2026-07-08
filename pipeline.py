"""Per-company OSINT pipeline: search -> fetch -> analyze -> (optional) AI.

Returns a plain dict per company:
    {"company": Company, "jobs": [Job, ...], "generated": [(Job, docs), ...]}
"""
import asyncio

from crawler.search import search_company
from crawler.downloader import fetch
from crawler.intelligence import analyze_site
from models.company import Company
from models.job import Job


def _build_company(name, data):
    ats_detected = data.get("ats_detected", [])
    careers = data.get("careers_pages", [])
    internships = data.get("internship_pages", [])
    blogs = data.get("blogs", [])
    socials = data.get("socials", {})

    providers = sorted({a["provider"] for a in ats_detected})

    return Company(
        name=name,
        website=data.get("url"),
        career_page=careers[0] if careers else None,
        ats=", ".join(providers) if providers else None,
        github=socials.get("github"),
        linkedin=socials.get("linkedin"),
        engineering_blog=blogs[0] if blogs else None,
        internships=internships[0] if internships else None,
        emails=data.get("emails", []),
        socials=socials,
        job_pages=careers,
    )


def _build_jobs(name, data):
    jobs = []
    for j in data.get("jobs_found", []):
        title = (j.get("title") or "").strip()
        if not title:
            continue
        jobs.append(Job(
            title=title,
            company=name,
            location=j.get("location"),
            url=j.get("url"),
            description=(j.get("description") or ""),
        ))
    return jobs


async def process_company(name, use_ai=False, profile=None, generate_top=0):
    result = {"company": Company(name=name), "jobs": [], "generated": []}

    print(f"-> {name}: searching...")
    websites = await asyncio.to_thread(search_company, name)
    if not websites:
        print(f"   {name}: no website found")
        return result

    website = websites[0]
    result["company"].website = website

    page = await fetch(website)
    if not page:
        print(f"   {name}: fetch failed ({website})")
        return result

    # analyze_site is synchronous (BeautifulSoup + sync ATS requests); run it
    # off the event loop so companies still process concurrently.
    data = await asyncio.to_thread(analyze_site, page["url"], page["html"])

    company = _build_company(name, data)
    jobs = _build_jobs(name, data)

    if use_ai and jobs:
        from ai.pipeline import score_jobs
        jobs = await asyncio.to_thread(score_jobs, jobs, data, profile)

        if generate_top > 0:
            from ai.pipeline import generate_documents
            for job in jobs[:generate_top]:
                docs = await asyncio.to_thread(generate_documents, job, profile)
                result["generated"].append((job, docs))

    result["company"] = company
    result["jobs"] = jobs

    print(f"   {name}: site={company.website} ats={company.ats or '-'} jobs={len(jobs)}")
    return result
