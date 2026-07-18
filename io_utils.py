"""Input/output helpers: read the company list, write the CSV outputs, and
write generated application documents."""
import csv
import re
from pathlib import Path

DEFAULT_PROFILE = (
    "Software engineer with experience in Python, backend systems, APIs, "
    "distributed systems and cloud infrastructure. Comfortable with async "
    "programming, data pipelines and building internal tooling. Looking for "
    "backend / platform / infrastructure roles."
)


def read_companies(path):
    """Read company names from a text file (one per line, '#' comments)."""
    p = Path(path)
    if not p.exists():
        return []
    companies = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        companies.append(line)
    return companies


def load_profile(path):
    """Load the user profile text used for AI scoring/generation."""
    p = Path(path)
    if p.exists():
        # Drop comment lines so a '#' note in profile.txt is not scored.
        lines = [
            ln for ln in p.read_text(encoding="utf-8").splitlines()
            if not ln.strip().startswith("#")
        ]
        text = "\n".join(lines).strip()
        if text:
            return text
    return DEFAULT_PROFILE


COMPANY_COLUMNS = [
    "company", "website", "description",
    "founded", "hq_location", "employee_count", "tech_stack",
    "careers_page", "ats", "num_jobs", "hiring_breakdown", "internships",
    "emails", "phones", "security_contact", "github", "linkedin", "other_socials",
    "engineering_blog", "rss_feed", "logo",
]

JOB_COLUMNS = [
    "company", "title", "location", "department", "employment_type",
    "remote", "posted", "url",
    "role_type", "role_confidence", "match_score", "company_score", "final_score",
]

# Social platforms that already have their own dedicated column.
_DEDICATED_SOCIALS = {"github", "linkedin"}


def _join(values, limit=5):
    values = [v for v in (values or []) if v]
    return "; ".join(values[:limit])


def _other_socials(socials):
    """Join social profiles that don't have a dedicated column, as 'name=url'."""
    items = [
        f"{name}={url}"
        for name, url in (socials or {}).items()
        if name not in _DEDICATED_SOCIALS and url
    ]
    return "; ".join(items)


def write_companies_csv(path, results):
    path = Path(path)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COMPANY_COLUMNS)
        writer.writeheader()
        for r in results:
            c = r["company"]
            writer.writerow({
                "company": c.name,
                "website": c.website or "",
                "description": c.description or "",
                "founded": c.founded or "",
                "hq_location": c.hq_location or "",
                "employee_count": c.employee_count or "",
                "tech_stack": _join(c.tech_stack, limit=20),
                "careers_page": c.career_page or "",
                "ats": c.ats or "",
                "num_jobs": len(r["jobs"]),
                "hiring_breakdown": c.hiring_breakdown or "",
                "internships": "yes" if c.internships else "no",
                "emails": _join(c.emails),
                "phones": _join(c.phones),
                "security_contact": _join(c.security_contact),
                "github": c.github or "",
                "linkedin": c.linkedin or "",
                "other_socials": _other_socials(c.socials),
                "engineering_blog": c.engineering_blog or "",
                "rss_feed": _join(c.feeds),
                "logo": c.logo or "",
            })
    return len(results)


def write_jobs_csv(path, results):
    path = Path(path)
    count = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=JOB_COLUMNS)
        writer.writeheader()
        for r in results:
            for job in r["jobs"]:
                writer.writerow({
                    "company": job.company or r["company"].name,
                    "title": job.title,
                    "location": job.location or "",
                    "department": job.department or "",
                    "employment_type": job.employment_type or "",
                    "remote": job.remote or "",
                    "posted": job.posted or "",
                    "url": job.url or "",
                    # AI columns stay blank when scoring was not run.
                    "role_type": job.role_type or "",
                    "role_confidence": round(job.role_confidence, 4) if job.role_confidence else "",
                    "match_score": job.match_score or "",
                    "company_score": job.company_score or "",
                    "final_score": job.final_score or "",
                })
                count += 1
    return count


def _slug(text):
    text = re.sub(r"[^\w\s-]", "", (text or "").lower())
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text or "item"


def write_generated_docs(directory, results):
    """Write one markdown file per generated job document."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    count = 0
    for r in results:
        for i, (job, docs) in enumerate(r["generated"], start=1):
            filename = f"{_slug(job.company)}_{i}_{_slug(job.title)}.md"
            content = (
                f"# {job.title}\n\n"
                f"**Company:** {job.company}\n\n"
                f"**Location:** {job.location or '-'}\n\n"
                f"**URL:** {job.url or '-'}\n\n"
                f"**Final score:** {job.final_score}\n\n"
                f"## Resume bullets\n\n{docs.get('resume_bullets', '')}\n\n"
                f"## Cover letter\n\n{docs.get('cover_letter', '')}\n\n"
                f"## Recruiter message\n\n{docs.get('recruiter_message', '')}\n"
            )
            (directory / filename).write_text(content, encoding="utf-8")
            count += 1
    return count
