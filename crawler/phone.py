"""Extract phone numbers from page HTML.

Precision over recall: we trust explicit `tel:` links first (unambiguous), then
fall back to a conservative scan for internationally-formatted numbers (leading
`+`) in the visible text. We deliberately avoid a greedy national-format regex
so we don't harvest dates, IDs, or product codes.
"""
import re
from urllib.parse import unquote

# `tel:` / `callto:` links are the most reliable signal a site gives us.
_TEL_RE = re.compile(r'(?:tel|callto):([+()\d][\d\-\s().]{5,}\d)', re.IGNORECASE)

# International-format numbers in free text (must start with +country code).
_INTL_RE = re.compile(r'(?<![\w+])\+\d[\d\-\s().]{6,}\d')


def _digits(num):
    return re.sub(r"\D", "", num)


def _normalize(num):
    """Strip formatting but keep a leading '+' for international numbers."""
    num = unquote(num).strip()
    plus = num.lstrip().startswith("+")
    core = _digits(num)
    return ("+" + core) if plus else core


def _plausible(num):
    n = len(_digits(num))
    return 7 <= n <= 15  # E.164 allows up to 15 digits.


def extract_phones(html):
    """Return a de-duplicated list of phone numbers found in the HTML."""
    html = html or ""
    found, seen = [], set()

    def _add(raw):
        num = _normalize(raw)
        key = _digits(num)
        if _plausible(num) and key not in seen:
            seen.add(key)
            found.append(num)

    for raw in _TEL_RE.findall(html):
        _add(raw)
    for raw in _INTL_RE.findall(html):
        _add(raw)

    return found
