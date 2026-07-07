def compute_final_score(job):

    # weights (tune later)
    match_weight = 0.5
    company_weight = 0.3
    role_weight = 0.2

    role_bonus = job.role_confidence * 100

    final = (
        job.match_score * match_weight +
        job.company_score * company_weight +
        role_bonus * role_weight
    )

    return round(final, 2)