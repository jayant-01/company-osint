"""Parse an RFC 9116 security.txt file for its security-contact details.

security.txt is a plain-text file a site publishes at a well-known path to tell
researchers how to report vulnerabilities. We only trust responses that look
like a real security.txt (a `Contact:` field, not an HTML 404 page).
"""
import re

# Where security.txt lives, in order of preference (RFC 9116).
SECURITY_PATHS = ("/.well-known/security.txt", "/security.txt")

_CONTACT_RE = re.compile(r"^\s*contact:\s*(.+)$", re.IGNORECASE | re.MULTILINE)


def parse_security_txt(text):
    """Return the Contact values from a security.txt body (empty if not valid)."""
    if not text:
        return []
    low = text.lower()
    # A missing file usually redirects to an HTML page; that's not security.txt.
    if any(marker in low for marker in ("<html", "<!doctype", "<body")):
        return []

    contacts, seen = [], set()
    for raw in _CONTACT_RE.findall(text):
        value = raw.split("#", 1)[0].strip()  # drop trailing comments
        if value and value not in seen:
            seen.add(value)
            contacts.append(value)
    return contacts
