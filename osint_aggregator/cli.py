"""Click-based entry point: runs whichever modules were asked for, 
correlates the results, and renders json/md/html output."""

import json
import logging
import os
import re
import sys
from dataclasses import asdict
from datetime import datetime, timezone

import click
from jinja2 import Environment, FileSystemLoader

from .correlate import find_correlations
from .modules import breach as breach_module
from .modules import domain as domain_module
from .modules import username as username_module
from .schema import Report

"""Resolve templates relative to this file's location, not the CWD.
otherwise this breaks the moment it's run from anywhere other than inside the repo
For example it would break once it becomes pip-installed"""

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

def _run_modules(report, username=None, domain=None, email=None):
    if username:
            username_module.run(username, report)
    if domain:
            domain_module.run(domain, report)
    if email:
            breach_module.run(email, report)


def _write_output(report, username, domain, email, out, output_format):
    findings_dicts = [asdict(f) for f in report.findings]

    if output_format in ("json", "all"):
        with open(f"{out}.json", "w") as f:
            json.dump(findings_dicts, f, indent=2)

    if output_format in ("md", "html", "all"):
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        context = dict(
            findings=findings_dicts,
            generated_at=datetime.now(timezone.utc).isoformat(),
            username=username, domain=domain, email=email,
        )
        if output_format in ("md", "all"):
            with open(f"{out}.md", "w") as f:
                f.write(env.get_template("report.md.j2").render(**context))
        if output_format in ("html", "all"):
            with open(f"{out}.html", "w") as f:
                f.write(env.get_template("report.html.j2").render(**context))


def _sanitize(target):
    """Turn a target string into something safe to use as a filename."""
    return re.sub(r"[^a-zA-Z0-9.-]", "_", target)

@click.command()
@click.option("--username", default=None)
@click.option("--domain", default=None)
@click.option("--email", default=None)
@click.option("--out", default="report", help="Output base filename, without extension")
@click.option("--output", "output_format", type=click.Choice(["json", "md", "html", "all"]), default="all")
@click.option("--verbose", is_flag=True, default=False)
@click.option("--stdin", "read_stdin", is_flag=True, default=False, help="Read targets from stdin, one per line")
@click.option("--type", "stdin_type", type=click.Choice(["username", "domain", "email"]), default=None,
              help="What kind of targets are being piped in via --stdin")
def recon(username, domain, email, out, output_format, verbose, read_stdin, stdin_type):
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(levelname)s [%(name)s] %(message)s",
    )

    if read_stdin:
        if not stdin_type:
            raise click.UsageError("--type is required when using --stdin (username, domain, or email)")
        targets = [line.strip() for line in sys.stdin if line.strip()]
        for target in targets:
            kwargs = {stdin_type: target}
            report = Report()
            _run_modules(report, **kwargs)
            find_correlations(report, **kwargs)
            target_out = f"{out}_{_sanitize(target)}"
            _write_output(report, kwargs.get("username"), kwargs.get("domain"), kwargs.get("email"),
                          target_out, output_format)
            click.echo(f"{target}: {len(report.findings)} findings -> {target_out}.*")
        click.echo(f"Processed {len(targets)} targets from stdin.")
        return

    report = Report()
    _run_modules(report, username=username, domain=domain, email=email)
    find_correlations(report, username=username, domain=domain, email=email)
    _write_output(report, username, domain, email, out, output_format)
    click.echo(f"Collected {len(report.findings)} findings. Output: {output_format} ({out}.*)")


if __name__ == "__main__":
    recon()