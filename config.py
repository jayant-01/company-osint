from pathlib import Path

BASE_DIR = Path(__file__).parent

OUTPUT_DIR = BASE_DIR / "output"

CACHE_DIR = BASE_DIR / ".cache"

HEADERS = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/138 Safari/537.36"
}

REQUEST_TIMEOUT = 30

MAX_REDIRECTS = 5

MAX_CONCURRENT_REQUESTS = 20