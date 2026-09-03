from osint_aggregator.schema import Report
from osint_aggregator.correlate import find_correlations

def test_username_email_local_part_match():
    notes = find_correlations(Report(), username="foo", email="foo@example.com")
    assert any("matches the username" in n for n in notes)

def test_no_match_when_unrelated():
    notes = find_correlations(Report(), username="torvalds", domain="example.com", email="test@example.com")
    assert notes == []

def test_whois_email_direct_match():
    report = Report()
    report.add("domain", "example.com", "whois_email", "someone@example.com", confidence=0.7)
    notes = find_correlations(report, email="someone@example.com")
    assert any("appears directly in the domain's WHOIS" in n for n in notes)