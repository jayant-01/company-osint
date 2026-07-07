from pydantic import BaseModel


class Company(BaseModel):
    name: str
    website: str | None = None
    career_page: str | None = None
    ats: str | None = None
    github: str | None = None
    linkedin: str | None = None
    engineering_blog: str | None = None
    internships: str | None = None
    emails: list[str] = []
    phones: list[str] = []
    socials: dict = {}
    job_pages: list[str] = []