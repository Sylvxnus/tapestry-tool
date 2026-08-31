import click
from .schema import Report

@click.command()
@click.option("--username", default=None)
@click.option("--domain", default=None)
@click.option("--email", default=None)
@click.option("--out", default="report.json")
def recon(username, domain, email, out):
    report = Report()
    # Just a really basic structure atm, I shall be addimg stuff later on this week :)
    click.echo(f"Collected {len(report.findings)} findings so far.")

if __name__ == "__main__":
    recon()