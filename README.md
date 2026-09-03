# Tapestry

[![CI](https://github.com/Sylvxnus/tapestry-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/Sylvxnus/tapestry-tool/actions/workflows/ci.yml)

<img width="848" height="380" alt="Screenshot 2026-09-03 170957" src="https://github.com/user-attachments/assets/1ae8cd2a-b27e-446e-888e-c5722bd6094e" />


A custom OSINT aggregator that pulls and correlates data from multiple public sources — usernames, domain/infra records, and known data breaches — into a single, correlated report.

Built as a CTF OSINT practice and portfolio project. Everything it does is a passive, public lookup — no active scanning, no brute forcing, no bypassing authentication. See [Ethical use](#ethical-use) below before running it against anything.

## Features

- **Username recon** — checks whether a username exists across a small curated set of platforms (GitHub, Docker Hub, dev.to, Steam), using verified detection logic rather than guessing at each site's behaviour
- **Domain/infra recon** — WHOIS, DNS records (A/AAAA/MX/TXT/NS), subdomain enumeration via crt.sh's Certificate Transparency logs, and passive header fingerprinting
- **Breach checking** — free, no-API-key email breach lookup via XposedOrNot
- **Correlation engine** — cross-references findings across sources (e.g. an email's local-part matching a username, or a username appearing in a domain's WHOIS record) and flags likely-same-identity matches
- **Multiple report formats** — JSON (machine-readable), Markdown, and styled HTML, chosen with `--output`
- **Unix-pipeable** — feed a list of targets through `--stdin` instead of one at a time
- **Fully free** — every source used is either a public record, a passive lookup, or a free/no-key API

## Installation

```powershell
git clone https://github.com/Sylvxnus/tapestry-tool.git
cd tapestry-tool
python -m venv venv
venv\Scripts\Activate.ps1   # macOS/Linux: source venv/bin/activate
pip install -e ".[dev]"
```

This installs the `tapestry` command into your environment (editable mode — code changes take effect immediately, no reinstall needed).

## Usage

```powershell
tapestry --username torvalds
tapestry --domain example.com
tapestry --email someone@example.com

# combine sources to enable correlation
tapestry --username foo --email foo@example.com

# choose output format and filename
tapestry --username torvalds --output html --out my-report

# see what's happening under the hood
tapestry --domain example.com --verbose

# pipe many targets of the same type through stdin
Get-Content usernames.txt | tapestry --stdin --type username
```

Run `tapestry --help` for the full option list.

## Architecture

Each source is a self-contained module (`osint_aggregator/modules/`) exposing a single `run(target, report)` function. Every finding — regardless of which module produced it — gets written into one shared `Report` object (`schema.py`) as a `Finding(source, target, field, value, confidence, timestamp)`. That shared schema is what makes this an *aggregator* rather than three separate scripts: `correlate.py` can scan across all findings from all sources afterward, looking for overlaps (matching emails, usernames appearing in WHOIS records, etc.) without needing to know the internals of any individual module.

`cli.py` (built on Click) wires it together: it runs whichever modules were requested, runs correlation, then renders the combined findings through Jinja2 templates (`templates/`) into JSON, Markdown, and/or HTML.

### `osint_aggregator/`
- `schema.py` — shared Finding/Report data model
- `correlate.py` — cross-source correlation logic
- `cli.py` — Click entry point, output rendering
- `config.py` — tunables (timeouts, concurrency, site list)

### `modules/`
- `username.py` — cross-platform username existence checks
- `domain.py` — WHOIS, DNS, crt.sh subdomains, fingerprinting
- `breach.py` — XposedOrNot breach lookup

### `templates/`
Jinja2 report templates (Markdown, HTML)

## Development

```powershell
pytest -v          # run tests
ruff check .        # lint
```

CI runs both automatically on every push/PR via GitHub Actions.

## Ethical use

Everything this tool does is a passive, public lookup — no active scanning, no brute forcing, no bypassing authentication:

- Username checks are ordinary HTTP requests, the same as visiting the page in a browser
- Domain/infra data comes from public WHOIS and DNS records, plus Certificate Transparency logs (crt.sh) — a public log of previously issued certificates, not a scan of the target
- Breach checks use a free, public API (XposedOrNot) that only reports whether an email appears in already-known, previously disclosed breaches

**Only run this against targets you own, control, or have explicit permission to investigate** — your own accounts/domains, or CTF/training targets designed for the purpose. Running recon tools against third parties without authorization can violate computer misuse laws and the terms of service of the platforms being queried, even when each individual lookup is passive.

## Roadmap

Ideas logged but not built yet:

- Web dashboard (Flask/FastAPI front-end reusing the same collector modules)
- Wayback Machine tie-in for historical domain snapshots
- Image metadata (EXIF) module
- More username-recon sites via proper authenticated APIs (GitLab, Reddit) rather than page-scraping
- Mixed-type `--stdin` input (currently one target type per run)
