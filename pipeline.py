"""Per-company OSINT pipeline: search -> fetch -> analyze -> (optional) AI.

Returns a plain dict per company:
    {"company": Company, "jobs": [Job, ...], "generated": [(Job, docs), ...]}
"""
import asyncio
from urllib.parse import urlsplit

from crawler.search import search_company
from crawler.downloader import fetch
from crawler.intelligence import analyze_site
from crawler.utils import registered_domain
from crawler.roles import hiring_breakdown
from crawler.security_txt import SECURITY_PATHS, parse_security_txt
from models.company import Company
from models.job import Job

# How many same-domain careers pages to follow when the homepage has no ATS.
MAX_CAREERS_CRAWL = 2


def _build_company(name, data):
    ats_detected = data.get("ats_detected", [])
    careers = data.get("careers_pages", [])
    internships = data.get("internship_pages", [])
    blogs = data.get("blogs", [])
    socials = data.get("socials", {})

    providers = sorted({a["provider"] for a in ats_detected})
    titles = [j.get("title") for j in data.get("jobs_found", [])]

    return Company(
        name=name,
        website=data.get("url"),
        description=data.get("description") or None,
        career_page=careers[0] if careers else None,
        ats=", ".join(providers) if providers else None,
        github=socials.get("github"),
        linkedin=socials.get("linkedin"),
        engineering_blog=blogs[0] if blogs else None,
        internships=internships[0] if internships else None,
        emails=data.get("emails", []),
        phones=data.get("phones", []),
        security_contact=data.get("security_contact", []),
        socials=socials,
        job_pages=careers,
        feeds=data.get("feeds", []),
        founded=data.get("founded"),
        hq_location=data.get("hq_location"),
        employee_count=data.get("employee_count"),
        logo=data.get("logo"),
        tech_stack=data.get("tech_stack", []),
        hiring_breakdown=hiring_breakdown(titles) or None,
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
            department=j.get("department"),
            employment_type=j.get("employment_type"),
            remote=j.get("remote"),
            posted=j.get("posted"),
        ))
    return jobs


async def _analyze_url(url):
    """Fetch a URL and run the (synchronous) site analysis off the event loop."""
    page = await fetch(url)
    if not page:
        return None
    return await asyncio.to_thread(analyze_site, page["url"], page["html"])


async def _fetch_security_contacts(site_url):
    """Look up the site's security.txt (RFC 9116) and return its Contact values."""
    parts = urlsplit(site_url or "")
    if not parts.scheme or not parts.netloc:
        return []
    origin = f"{parts.scheme}://{parts.netloc}"
    for path in SECURITY_PATHS:
        page = await fetch(origin + path)
        if not page:
            continue
        contacts = parse_security_txt(page["html"])
        if contacts:
            return contacts
    return []


def _uniq(seq):
    out, seen = [], set()
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _merge_analysis(a, b):
    """Merge a second page's analysis into the first (homepage wins for scalars)."""
    merged = dict(a)
    merged["careers_pages"] = _uniq(a["careers_pages"] + b["careers_pages"])[:5]
    merged["internship_pages"] = _uniq(a["internship_pages"] + b["internship_pages"])[:5]
    merged["blogs"] = _uniq(a["blogs"] + b["blogs"])[:5]
    merged["feeds"] = _uniq(a.get("feeds", []) + b.get("feeds", []))[:5]
    merged["emails"] = _uniq(a["emails"] + b["emails"])[:10]
    merged["phones"] = _uniq(a.get("phones", []) + b.get("phones", []))[:10]
    merged["tech_stack"] = _uniq(a.get("tech_stack", []) + b.get("tech_stack", []))

    # Homepage (a) wins for scalars; the careers page fills any gaps.
    for key in ("description", "founded", "hq_location", "employee_count", "logo"):
        merged[key] = a.get(key) or b.get(key)

    seen, ats = set(), []
    for x in a["ats_detected"] + b["ats_detected"]:
        k = (x["provider"], x["url"])
        if k not in seen:
            seen.add(k)
            ats.append(x)
    merged["ats_detected"] = ats

    seen, jobs = set(), []
    for j in a["jobs_found"] + b["jobs_found"]:
        ident = j.get("url") or j.get("title")
        if ident not in seen:
            seen.add(ident)
            jobs.append(j)
    merged["jobs_found"] = jobs[:20]

    socials = dict(b.get("socials", {}))
    socials.update(a.get("socials", {}))  # homepage socials win
    merged["socials"] = socials

    merged["total_links"] = a.get("total_links", 0) + b.get("total_links", 0)
    return merged


async def _crawl(website):
    """Analyze the homepage; if no ATS is found, follow same-domain careers pages."""
    data = await _analyze_url(website)
    if data is None:
        return None

    if data["ats_detected"]:
        return data

    site_domain = registered_domain(data["url"])
    candidates = [
        c for c in data["careers_pages"]
        if registered_domain(c) == site_domain and c != data["url"]
    ]

    for careers_url in candidates[:MAX_CAREERS_CRAWL]:
        sub = await _analyze_url(careers_url)
        if not sub:
            continue
        data = _merge_analysis(data, sub)
        if data["ats_detected"]:
            break

    return data


async def process_company(name, use_ai=False, profile=None, generate_top=0):
    result = {"company": Company(name=name), "jobs": [], "generated": []}

    print(f"-> {name}: searching...")
    websites = await asyncio.to_thread(search_company, name)
    if not websites:
        print(f"   {name}: no website found")
        return result

    website = websites[0]
    result["company"].website = website

    data = await _crawl(website)
    if data is None:
        print(f"   {name}: fetch failed ({website})")
        return result

    data["security_contact"] = await _fetch_security_contacts(data["url"])

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
