"""Username recon: checks a small curated set of platforms for an existing account.
Each site is checked either by HTTP status code (a clean 404 means "not found") or
by a "not found" message string, for sites that always return 200."""

import asyncio
import logging
import httpx
from ..schema import Report
from ..config import USERNAME_SITES, USERNAME_CONCURRENCY, USERNAME_TIMEOUT

logger = logging.getLogger(__name__)


def determine_exists(site, status_code, text):
    """Decide whether a username appears to exist, given the response. Kept separate
    from the actual network call so it's unit-testable without hitting the internet.

    For "message"-type sites, only a clean 200 is trusted — a rate-limit or block
    page (e.g. HackerNews's 429) won't contain the expected "not found" string either,
    which caused a real false-positive bug before this check was added.
    """
    if site["method"] == "status":
        return status_code < 400
    return status_code == 200 and site["not_found"].lower() not in text.lower()


async def check_site(client, sem, site, username, report):
    url = site["url"].format(username)
    async with sem:
        try:
            resp = await client.get(url, timeout=USERNAME_TIMEOUT, follow_redirects=True)
        except httpx.RequestError as e:
            logger.warning("%s skipped: %s", site["name"], e)
            return

    if determine_exists(site, resp.status_code, resp.text):
        report.add("username", username, "platform", site["name"], confidence=0.8)


async def run_async(username, report):
    headers = {"User-Agent": "Mozilla/5.0 (osint-aggregator; educational use)"}
    sem = asyncio.Semaphore(USERNAME_CONCURRENCY)
    async with httpx.AsyncClient(headers=headers) as client:
        await asyncio.gather(*(check_site(client, sem, s, username, report) for s in USERNAME_SITES))


def run(username, report):
    asyncio.run(run_async(username, report))