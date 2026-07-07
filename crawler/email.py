import re


EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}"


def extract_emails(html):
    return list(set(re.findall(EMAIL_REGEX, html)))