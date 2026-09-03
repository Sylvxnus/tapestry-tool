import httpx
import dns.resolver
import whois
from ..schema import Report


TIMEOUT = 8.0


def check_whois(domain, report):
    # Sends a WHOIS query to the registry and parses the response into an object with attributes
    try:
        w = whois.whois(domain)
    except Exception as e:
        print(f"[domain] whois lookup failed: {e}")
        return


    # Each of these is "if the field gets populated add it to the report at the end"
    # We need to have the str() wrapping as sometimes fields might come back as Python objects
    # and report.add expects a string value
    if w.registrar:
        report.add("domain", domain, "registrar", str(w.registrar), confidence=0.9)
    if w.creation_date:
        report.add("domain", domain, "created", str(w.creation_date), confidence=0.9)
    if w.org:
        report.add("domain", domain, "org", str(w.org), confidence=0.7)
    if w.emails:
        emails = w.emails if isinstance(w.emails, list) else [w.emails]
        for email in emails:
            report.add("domain", domain, "whois_email", str(email), confidence=0.7)

def check_dns(domain, report):
    for rtype in ["A", "AAAA", "MX", "TXT", "NS"]:
        try:
            answers = dns.resolver.resolve(domain, rtype, lifetime=TIMEOUT)
            for rdata in answers:
                report.add("domain", domain, f"dns_{rtype}", str(rdata), confidence=1.0)
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            continue
        except Exception as e:
            print(f"[domain] DNS {rtype} lookup failed: {e}")


def check_subdomains(domain, report):
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    try:
        resp = httpx.get(url, timeout=15.0)
        resp.raise_for_status()
        entries = resp.json()

    except Exception as e:
        print(f"[domain] crt.sh lookup failed (its a slow and flakey service, sometimes just retry): {e}")
        return

    seen = set()
    for entry in entries:
        for sub in entry.get("name_value", "").split("\n"):
            sub = sub.strip().lower()
            if not sub or sub in seen:
                continue
            if sub != domain and not sub.endswith("." + domain):
                continue
            if "@" in sub or " " in sub:
                continue
            seen.add(sub)
            report.add("domain", domain, "subdomain", sub, confidence=0.85)



def check_fingerprint(domain, report):
    headers = {"User-Agent": "Mozilla/5.0 (osint-aggregator; educational use)"}
    for scheme in ("https", "http"):
        try:
            resp = httpx.get(f"{scheme}://{domain}", headers=headers, timeout=TIMEOUT, follow_redirects=True)
        except httpx.RequestError:
            continue
        if server := resp.headers.get("server"):
            report.add("domain", domain, "server_header", server, confidence=0.7)
        if powered_by := resp.headers.get("x-powered-by"):
            report.add("domain", domain, "x_powered_by", powered_by, confidence=0.7)
        break

def run(domain, report):
    check_whois(domain, report)
    check_dns(domain, report)
    check_subdomains(domain, report)
    check_fingerprint(domain, report)