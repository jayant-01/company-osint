from ai.llm import generate


def generate_resume_bullets(job, user_profile):

    prompt = f"""
You are an expert resume writer.

User Profile:
{user_profile}

Job Title:
{job.title}

Job Description:
{job.description}

Task:
Rewrite the user's experience into 4 strong resume bullet points
tailored specifically for this job.

Make them:
- technical
- quantified
- ATS-friendly
- impact focused

Return only bullet points.
"""

    return generate(prompt)