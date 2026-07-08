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
    "company", "website", "careers_page", "ats", "num_jobs",
    "emails", "github", "linkedin", "engineering_blog", "internships",
]

JOB_COLUMNS = [
    "company", "title", "location", "url",
    "role_type", "role_confidence", "match_score", "company_score", "final_score",
]


def _join(values, limit=5):
    values = [v for v in (values or []) if v]
    return "; ".join(values[:limit])


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
                "careers_page": c.career_page or "",
                "ats": c.ats or "",
                "num_jobs": len(r["jobs"]),
                "emails": _join(c.emails),
                "github": c.github or "",
                "linkedin": c.linkedin or "",
                "engineering_blog": c.engineering_blog or "",
                "internships": "yes" if c.internships else "no",
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
