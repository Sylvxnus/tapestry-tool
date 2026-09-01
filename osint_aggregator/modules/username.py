import asyncio
import httpx
from ..schema import Report

SITES = [
    {"name": "GitHub",     "url": "https://github.com/{}",                       "method": "status"},
    {"name": "Docker Hub", "url": "https://hub.docker.com/v2/users/{}/",         "method": "status"},
    {"name": "dev.to",     "url": "https://dev.to/api/users/by_username?url={}", "method": "status"},
    {"name": "Steam",      "url": "https://steamcommunity.com/id/{}",            "method": "message", "not_found": "The specified profile could not be found."},
]

CONCURRENCY = 5
TIMEOUT = 8.0

async def check_site(client, sem, site, username, report):
    url = site["url"].format(username)
    async with sem:
        try:
            resp = await client.get(url, timeout=TIMEOUT, follow_redirects=True)
        except httpx.RequestError as e:
            print(f"[username] {site['name']} skipped: {e}")
            return

    if site["method"] == "status":
        exists = resp.status_code < 400
    else:  # "message" only trust this on a clean 200, not an error
        exists = resp.status_code == 200 and site["not_found"].lower() not in resp.text.lower()

    if exists:
        report.add("username", username, "platform", site["name"], confidence=0.8)

async def run_async(username, report):
    headers = {"User-Agent": "Mozilla/5.0 (osint-aggregator; educational use)"}
    sem = asyncio.Semaphore(CONCURRENCY)
    async with httpx.AsyncClient(headers=headers) as client:
        await asyncio.gather(*(check_site(client, sem, s, username, report) for s in SITES))

def run(username, report):
    asyncio.run(run_async(username, report))