import json
from dataclasses import asdict
import click
from .schema import Report
from .modules import username as username_module
from .modules import domain as domain_module

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
    # The next lines are for later when i implement the domain and email chaining logic
    # if email -> modules.breach.run(email, report)

    with open(out, "w") as f:
        json.dump([asdict(finding) for finding in report.findings], f, indent=2)

    click.echo(f"Collected {len(report.findings)} findings. Written to {out}")

if __name__ == "__main__":
    recon()