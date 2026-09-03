import httpx 
from ..schema import Report

TIMEOUT = 8.0

def run(email, report):
    url = f"https://api.xposedornot.com/v1/check-email/{email}"
    try:
        resp = httpx.get(url, timeout=TIMEOUT)
    except httpx.RequestError as e:
        print(f"[brech] XposedOrNot lookup failed: {e}")
        return

    if resp.status_code == 404:
        return

    try:
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[breach] XposedOrNot response error: {e}")
        return

    breach_lists = data.get("breaches", [])
    names = breach_lists[0] if breach_lists else []

    for name in names:
        report.add("breach", email, "breach_name", str(name), cofidence=0.9)