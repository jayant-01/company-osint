def compute_company_score(data):

    score = 0

    # ATS presence = strong hiring signal
    if data.get("ats_detected"):
        score += 20

    # number of jobs
    jobs = len(data.get("jobs_found", []))

    if jobs > 50:
        score += 30
    elif jobs > 20:
        score += 20
    elif jobs > 5:
        score += 10

    # internships
    if data.get("internship_pages"):
        score += 10

    # engineering blog
    if data.get("blogs"):
        score += 10

    # emails found
    if data.get("emails"):
        score += 10

    # GitHub presence
    if data.get("socials", {}).get("github"):
        score += 5

    return min(score, 100)