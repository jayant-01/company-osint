from ai.resume import generate_resume_bullets
from ai.cover_letter import generate_cover_letter
from ai.outreach import generate_recruiter_message


def enrich_with_ai_outputs(job, user_profile):

    job.resume_bullets = generate_resume_bullets(job, user_profile)

    job.cover_letter = generate_cover_letter(job, user_profile)

    job.recruiter_message = generate_recruiter_message(job, user_profile)

    return job