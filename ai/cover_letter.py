from ai.llm import generate


def generate_cover_letter(job, user_profile):

    prompt = f"""
Write a concise professional cover letter.

User Profile:
{user_profile}

Job Title:
{job.title}

Company:
{job.company}

Job Description:
{job.description}

Requirements:
- 150-200 words
- professional tone
- mention skills match
- no fluff
- strong opening and closing
"""

    return generate(prompt)