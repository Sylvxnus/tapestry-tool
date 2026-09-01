import asyncio
import httpx
from ..schema import Report

# "status": non-2xx = not found (cleanest, should be the most reliable im hoping)
# "message": site always returns 200, but shows a giveaway string when the profile doesn't exist
SITES = [
    {"name": "GitHub",     "url": "https://github.com/{}",                      "method": "status"},
    {"name": "GitLab",     "url": "https://gitlab.com/{}",                       "method": "status"},
    {"name": "Reddit",     "url": "https://www.reddit.com/user/{}/about.json",   "method": "status"},
    {"name": "PyPI",       "url": "https://pypi.org/user/{}/",                   "method": "status"},
    {"name": "Docker Hub", "url": "https://hub.docker.com/v2/users/{}/",         "method": "status"},
    {"name": "dev.to",     "url": "https://dev.to/api/users/by_username?url={}", "method": "status"},
    {"name": "CodePen",    "url": "https://codepen.io/{}",                       "method": "status"},
    {"name": "HackerNews", "url": "https://news.ycombinator.com/user?id={}",     "method": "message", "not_found": "No such user"},
    {"name": "Steam",      "url": "https://steamcommunity.com/id/{}",            "method": "message", "not_found": "The specified profile could not be found"},
]

CONCURRENCY = 5   # keep this low, otherwise we are hammering peoples sites
TIMEOUT = 8.0

async def check_site(client, sem, site, username, report):
    url = site["url"].format(username)
    async with sem:
        try:
            resp = await client.get(url, timeout=TIMEOUT, follow_redirects=True)
        except httpx.RequestError:
            return  # unreachable/timed out — skip rather than false positive

    if site["method"] == "status":
        exists = resp.status_code < 400
    else:
        exists = site["not_found"].lower() not in resp.text.lower()

    if exists:
        report.add("username", username, "platform", site["name"], confidence=0.8)

async def run_async(username, report):
    headers = {"User-Agent": "Mozilla/5.0 (osint-aggregator; educational use)"}
    sem = asyncio.Semaphore(CONCURRENCY)
    async with httpx.AsyncClient(headers=headers) as client:
        await asyncio.gather(*(check_site(client, sem, s, username, report) for s in SITES))

def run(username, report):
    asyncio.run(run_async(username, report))