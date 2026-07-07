from ai.llm import generate


def generate_recruiter_message(job, user_profile):

    prompt = f"""
Write a short LinkedIn message to a recruiter.

Context:
- Job: {job.title}
- Company: {job.company}
- User Profile: {user_profile}

Rules:
- 3-5 lines max
- polite
- direct
- request referral or guidance
- no over-explaining
"""

    return generate(prompt)