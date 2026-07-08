from crawler.link_extractor import extract_links
from crawler.ats import detect_ats
from crawler.email import extract_emails
from crawler.ats_router import extract_jobs
from crawler.social import extract_socials


def analyze_site(base_url, html):

    links = extract_links(base_url, html)

    ats = detect_ats(links)

    emails = extract_emails(html)

    jobs = extract_jobs(ats, html)

    socials = extract_socials(links)

    careers = [l for l in links if "career" in l.lower() or "job" in l.lower()]

    internships = [l for l in links if "intern" in l.lower()]

    blogs = [l for l in links if "blog" in l.lower() or "engineering" in l.lower()]

    return {
        "url": base_url,
        "careers_pages": careers[:5],
        "internship_pages": internships[:5],
        "ats_detected": ats,
        "jobs_found": jobs[:20],
        "emails": emails[:10],
        "socials": socials,
        "blogs": blogs[:5],
        "total_links": len(links),
    }
