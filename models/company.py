from pydantic import BaseModel


class Company(BaseModel):
    name: str
    website: str | None = None
    description: str | None = None
    career_page: str | None = None
    ats: str | None = None
    github: str | None = None
    linkedin: str | None = None
    engineering_blog: str | None = None
    internships: str | None = None
    emails: list[str] = []
    phones: list[str] = []
    security_contact: list[str] = []
    socials: dict = {}
    job_pages: list[str] = []
    feeds: list[str] = []
    # Firmographics from JSON-LD structured data.
    founded: str | None = None
    hq_location: str | None = None
    employee_count: str | None = None
    logo: str | None = None
    # Heuristic enrichment.
    tech_stack: list[str] = []
    hiring_breakdown: str | None = None