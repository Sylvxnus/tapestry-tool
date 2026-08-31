from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class Finding:
    source: str          # "username" | "domain" | "breach"
    target: str           # the value thats been queried
    field: str             # e.g. "platform", "dns_record", "breach_name"
    value: str
    confidence: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def add(self, source: str, target: str, field_name: str, value: str, confidence: float = 1.0):
        self.findings.append(Finding(source, target, field_name, value, confidence))