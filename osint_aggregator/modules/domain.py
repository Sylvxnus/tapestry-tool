import logging
import httpx
import dns.resolver
import whois
from ..schema import Report
from ..config import DOMAIN_TIMEOUT, CRTSH_TIMEOUT

logger = logging.getLogger(__name__)

def check_whois(domain, report):
    try:
        w = whois.whois(domain)
    except Exception as e:
        logger.warning("whois lookup failed: %s", e)
        return
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
            answers = dns.resolver.resolve(domain, rtype, lifetime=DOMAIN_TIMEOUT)
            for rdata in answers:
                report.add("domain", domain, f"dns_{rtype}", str(rdata), confidence=1.0)
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            continue
        except Exception as e:
            logger.warning("DNS %s lookup failed: %s", rtype, e)

def check_subdomains(domain, report):
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    try:
        resp = httpx.get(url, timeout=CRTSH_TIMEOUT)
        resp.raise_for_status()
        entries = resp.json()
    except Exception as e:
        logger.warning("crt.sh lookup failed (it's a slow/flaky service, sometimes just retry): %s", e)
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
            resp = httpx.get(f"{scheme}://{domain}", headers=headers, timeout=DOMAIN_TIMEOUT, follow_redirects=True)
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