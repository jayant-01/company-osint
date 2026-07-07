import aiohttp

from config import HEADERS


async def download(url):
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(url, allow_redirects=True) as response:
            html = await response.text(errors="ignore")
            return str(response.url), html