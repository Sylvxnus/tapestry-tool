def find_correlations(report, username=None, domain=None, email=None):
    correlations = []

    if username and email:
        local_part = email.split("@")[0].lower()
        if local_part == username.lower():
            correlations.append(
                f"Email local-part '{local_part}' matches the username '{username}' - likely the same person"
            )


    if email:
        whois_emails = [f.value.lower() for f in report.findings if f.field == "whois_email"]
        if email.lower() in whois_emails:
            correlations.append(
                f"'{email}' apprears directly in the domains WHOIS registration"
            )

    if username:
        for f in report.findings:
            if f.field in ("whois_email", "org") and username.lower() in f.value.lower():
                correlations.append(
                    f"Username '{username}' appears in domain WHOIS field '{f.field}' : '{f.value}'"
                )


    for note in correlations:
        report.add("correlation", "-", "note", note, confidence=0.6)


    return correlations