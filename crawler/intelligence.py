from crawler.link_extractor import extract_links
from crawler.ats import detect_ats
from crawler.email import extract_emails
from crawler.phone import extract_phones
from crawler.ats_router import extract_jobs
from crawler.social import extract_socials, merge_social_urls
from crawler.parser import extract_metadata
from crawler.structured import extract_org
from crawler.techstack import detect_tech
from crawler.feeds import extract_feeds


def analyze_site(base_url, html):

    links = extract_links(base_url, html)

    ats = detect_ats(links)

    emails = extract_emails(html)

    phones = extract_phones(html)

    jobs = extract_jobs(ats, html)

    socials = extract_socials(links)

    meta = extract_metadata(html)

    org = extract_org(html)

    # JSON-LD sameAs often lists social profiles the page didn't link directly.
    socials = merge_social_urls(socials, org.get("same_as", []))

    tech_stack = detect_tech(html)

    feeds = extract_feeds(base_url, html)

    careers = [l for l in links if "career" in l.lower() or "job" in l.lower()]

    internships = [l for l in links if "intern" in l.lower()]

    blogs = [l for l in links if "blog" in l.lower() or "engineering" in l.lower()]

    return {
        "url": base_url,
        "description": meta.get("description") or "",
        "careers_pages": careers[:5],
        "internship_pages": internships[:5],
        "ats_detected": ats,
        "jobs_found": jobs[:20],
        "emails": emails[:10],
        "phones": phones[:10],
        "socials": socials,
        "blogs": blogs[:5],
        "feeds": feeds[:5],
        "tech_stack": tech_stack,
        "founded": org.get("founded"),
        "hq_location": org.get("hq_location"),
        "employee_count": org.get("employee_count"),
        "logo": org.get("logo"),
        "total_links": len(links),
    }
