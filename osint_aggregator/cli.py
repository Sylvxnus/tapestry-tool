import json
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
@click.option("--out", default="report.json")
def recon(username, domain, email, out):
    report = Report()

    if username:
        username_module.run(username, report)
    if domain:
        domain_module.run(domain, report)
    if email:
        breach_module.run(email, report)

    find_correlations(report, username=username, domain=domain, email=email)

    with open(out, "w") as f:
        json.dump([asdict(finding) for finding in report.findings], f, indent=2)


    env = Environment(loader=FileSystemLoader("osint_aggregator/templates"))
    template = env.get_template("report.md.j2")
    rendered = template.render(
        findings=[asdict(finding) for finding in report.findings],
        generated_at=datetime.now(timezone.utc).isoformat(),
        username=username,
        domain=domain,
        email=email
    )

    md_path = out.rsplit(".", 1)[0]+ ".md"
    with open(md_path, "w") as f:
        f.write(rendered)

    click.echo(f"Collected {len(report.findings)} findings. Written to {out} and {md_path}")

if __name__ == "__main__":
    recon()