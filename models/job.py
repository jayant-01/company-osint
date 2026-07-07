from pydantic import BaseModel


class Job(BaseModel):

    title: str

    company: str | None = None

    location: str | None = None

    url: str | None = None

    description: str = ""

    role_type: str | None = None

    role_confidence: float = 0.0

    match_score: float = 0.0

    company_score: float = 0.0

    final_score: float = 0.0