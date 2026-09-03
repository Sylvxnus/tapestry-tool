"""Click-based entry point: runs whichever modules were asked for, correlates the results, and renders json/md/html output."""

import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
import click
from jinja2 import Environment, FileSystemLoader
from .schema import Report
from .modules import username as username_module
from .modules import domain as domain_module
from .modules import breach as breach_module
from .correlate import find_correlations

@click.command()
@click.option("--username", default=None)
@click.option("--domain", default=None)
@click.option("--email", default=None)
@click.option("--out", default="report", help="Output base filename, without extension")
@click.option("--output", "output_format", type=click.Choice(["json", "md", "html", "all"]), default="all")
@click.option("--verbose", is_flag=True, default=False)
def recon(username, domain, email, out, output_format, verbose):
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(levelname)s [%(name)s] %(message)s",
    )

    report = Report()

    if username:
        username_module.run(username, report)
    if domain:
        domain_module.run(domain, report)
    if email:
        breach_module.run(email, report)

    find_correlations(report, username=username, domain=domain, email=email)

    findings_dicts = [asdict(f) for f in report.findings]

    if output_format in ("json", "all"):
        with open(f"{out}.json", "w") as f:
            json.dump(findings_dicts, f, indent=2)

    if output_format in ("md", "html", "all"):
        env = Environment(loader=FileSystemLoader("osint_aggregator/templates"))
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

    click.echo(f"Collected {len(report.findings)} findings. Output: {output_format} ({out}.*)")

if __name__ == "__main__":
    recon()