"""Categorize job titles into coarse departments for a hiring breakdown.

Provider `department` fields are inconsistent (Greenhouse often omits them), so
we bucket by title keyword instead — provider-independent and good enough to
answer "what is this company actually hiring for right now?".
"""
from collections import Counter

# Order matters: first matching bucket wins. Keep the more specific buckets
# (data, design) ahead of broad ones (engineering).
_BUCKETS = [
    ("data", ("data scientist", "data engineer", "machine learning", " ml ",
              "analytics", "data analyst", " ai ", "researcher")),
    ("design", ("designer", "design ", "ux", "ui ", "product design")),
    ("product", ("product manager", "product owner", "program manager", " tpm")),
    ("engineering", ("engineer", "developer", "programmer", "devops", "sre",
                     "architect", "software", "backend", "frontend",
                     "full stack", "full-stack", "qa", "sdet")),
    ("sales", ("sales", "account executive", "account manager",
               "business development", " bdr", " sdr", "revenue")),
    ("marketing", ("marketing", "growth", "seo", "content", "brand",
                   "social media", "communications")),
    ("support", ("support", "customer success", "customer service",
                 "help desk", "solutions engineer")),
    ("operations", ("operations", "logistics", "supply chain", "office manager",
                    "facilities")),
    ("people", ("recruiter", "recruiting", "talent", "human resources",
                " hr ", "people ")),
    ("finance", ("finance", "accountant", "accounting", "controller",
                 "financial", "auditor")),
    ("legal", ("legal", "counsel", "attorney", "compliance", "paralegal")),
]


def categorize_role(title):
    """Return the department bucket for a job title (default: 'other')."""
    t = f" {(title or '').lower()} "
    for name, keywords in _BUCKETS:
        if any(k in t for k in keywords):
            return name
    return "other"


def hiring_breakdown(titles):
    """Summarize a list of job titles as 'engineering:12; sales:4; ...'."""
    counts = Counter(categorize_role(t) for t in titles if t)
    if not counts:
        return ""
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return "; ".join(f"{name}:{n}" for name, n in ordered)
