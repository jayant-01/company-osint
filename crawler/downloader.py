import aiohttp
from config import HEADERS, REQUEST_TIMEOUT
from crawler.cache import Cache

cache = Cache()


async def fetch(url):

    cached = cache.get(url)

    if cached:

        return {
            "url": url,
            "html": cached,
            "cached": True
        }

    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

    async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:

        try:

            async with session.get(url, allow_redirects=True) as r:

                html = await r.text(errors="ignore")

                final_url = str(r.url)

                cache.set(final_url, html)

                return {
                    "url": final_url,
                    "html": html,
                    "cached": False
                }

        except Exception:

            return None