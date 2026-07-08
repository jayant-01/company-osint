"""AI enrichment layer. Imported only when --ai / --generate is used.

The heavy model libraries (transformers / torch / sentence-transformers) are
imported lazily inside these functions, so importing this module is cheap.
"""
from ai.company_scoring import compute_company_score
from ai.decesion_engine import compute_final_score


def score_jobs(jobs, company_data, user_profile):
    """Classify + score a list of Job models in place. Returns them sorted by
    final_score (best first)."""
    from ai.hf_client import classify_job
    from ai.scoring import score_job

    company_score = compute_company_score(company_data)

    for job in jobs:
        text = f"{job.title} {job.description}".strip()
        classification = classify_job(text)
        job.role_type = classification["label"]
        job.role_confidence = classification["score"]
        job.match_score = score_job(text, user_profile)
        job.company_score = company_score
        job.final_score = compute_final_score(job)

    jobs.sort(key=lambda j: j.final_score, reverse=True)
    return jobs


def generate_documents(job, user_profile):
    """Generate resume bullets, a cover letter and a recruiter message for one
    job. Returns a dict of strings."""
    from ai.resume import generate_resume_bullets
    from ai.cover_letter import generate_cover_letter
    from ai.outreach import generate_recruiter_message

    return {
        "resume_bullets": generate_resume_bullets(job, user_profile),
        "cover_letter": generate_cover_letter(job, user_profile),
        "recruiter_message": generate_recruiter_message(job, user_profile),
    }
