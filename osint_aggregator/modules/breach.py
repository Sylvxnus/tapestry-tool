"""Email breach check via XposedOrNot — free, no API key required."""
import logging

import httpx

from ..config import BREACH_TIMEOUT

logger = logging.getLogger(__name__)

def run(email, report):
    url = f"https://api.xposedornot.com/v1/check-email/{email}"
    try:
        resp = httpx.get(url, timeout=BREACH_TIMEOUT)
    except httpx.RequestError as e:
        logger.warning("XposedOrNot lookup failed: %s", e)
        return

    if resp.status_code == 404:
        return

    try:
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.warning("XposedOrNot response error: %s", e)
        return

    breach_lists = data.get("breaches", [])
    names = breach_lists[0] if breach_lists else []

    for name in names:
        report.add("breach", email, "breach_name", str(name), confidence=0.9)