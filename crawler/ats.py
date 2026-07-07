ATS_PATTERNS = {
    "greenhouse": "greenhouse.io",
    "lever": "jobs.lever.co",
    "ashby": "ashbyhq.com",
    "workday": "myworkdayjobs.com",
    "smartrecruiters": "smartrecruiters.com",
    "bamboohr": "bamboohr.com",
    "teamtailor": "teamtailor.com",
    "jobvite": "jobvite.com",
    "icims": "icims.com",
    "recruitee": "recruitee.com",
}


def detect_ats(links):
    found = []
    for link in links:
        for name, pattern in ATS_PATTERNS.items():
            if pattern in link:
                found.append({
                    "provider": name,
                    "url": link
                })
    return found