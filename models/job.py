from pydantic import BaseModel


class Job(BaseModel):

    title: str

    company: str | None = None

    location: str | None = None

    url: str | None = None

    description: str = ""

    department: str | None = None

    employment_type: str | None = None

    remote: str | None = None

    posted: str | None = None

    role_type: str | None = None

    role_confidence: float = 0.0

    match_score: float = 0.0

    company_score: float = 0.0

    final_score: float = 0.0