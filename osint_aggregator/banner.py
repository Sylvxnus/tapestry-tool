"""Startup banner — a nod to the project's namesake: weaving multiple public
sources into one correlated report."""

import pyfiglet

WEAVE_LINE = "╱╲" * 30


def print_banner():
    print("\n")
    print(WEAVE_LINE[:60])
    print(pyfiglet.figlet_format("TAPESTRY", font="slant"))
    print("  OSINT aggregator — weaving public sources into one correlated report")
    print("\n")
    print(WEAVE_LINE[:60])
    print("\n")
    print( " Weaving in progress... ")