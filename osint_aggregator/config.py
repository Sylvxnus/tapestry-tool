import json
import os

USERNAME_CONCURRENCY = 5
USERNAME_TIMEOUT = 8.0
DOMAIN_TIMEOUT = 8.0
CRTSH_TIMEOUT = 15.0
BREACH_TIMEOUT = 8.0

SITES_FILE = os.path.join(os.path.dirname(__file__), "sites.json")


def load_sites(path=None):
    """Load the list of username-check sites from a JSON file.

    Defaults to the bundled site list (sites.json, shipped with the package).
    Pass a path to use a custom list instead. Each entry needs "name", "url",
    and "method" ("status" or "message"); "message" entries also need "not_found".
    """
    target = path or SITES_FILE
    with open(target, encoding="utf-8-sig") as f:
        sites = json.load(f)

    for site in sites:
        missing = {"name", "url", "method"} - site.keys()
        if missing:
            raise ValueError(f"Site entry {site} is missing required field(s): {', '.join(missing)}")
        if site["method"] not in ("status", "message"):
            raise ValueError(
                f"Site '{site['name']}' has unknown method '{site['method']}' (expected 'status' or 'message')"
            )
        if site["method"] == "message" and "not_found" not in site:
            raise ValueError(f"Site '{site['name']}' uses method 'message' but has no 'not_found' text")

    return sites