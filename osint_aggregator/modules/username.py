import asyncio
import logging
import httpx
from ..schema import Report
from ..config import USERNAME_SITES, USERNAME_CONCURRENCY, USERNAME_TIMEOUT


logger = logging.getLogger(__name__)

async def check_site(client, sem, site, username, report):
    url = site["url"].format(username)
    async with sem:
        try:
            resp = await client.get(url, timeout=USERNAME_TIMEOUT, follow_redirects=True)
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
    sem = asyncio.Semaphore(USERNAME_CONCURRENCY)
    async with httpx.AsyncClient(headers=headers) as client:
        await asyncio.gather(*(check_site(client, sem, s, username, report) for s in USERNAME_SITES))

def run(username, report):
    asyncio.run(run_async(username, report))