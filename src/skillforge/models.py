"""Typed data models used by the scanner."""

from dataclasses import asdict, dataclass, field
from typing import Any

REPORT_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class SkillMetadata:
    name: str
    description: str
    path: str


@dataclass(frozen=True)
class Finding:
    rule_id: str
    title: str
    severity: str
    confidence: str
    message: str
    evidence: str
    rule_reference: str
    file_path: str
    line: int


@dataclass
class ScanReport:
    scanner_version: str
    skill: SkillMetadata
    findings: list[Finding] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def finding_count(self) -> int:
        return len(self.findings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": REPORT_SCHEMA_VERSION,
            "scanner_version": self.scanner_version,
            "skill": asdict(self.skill),
            "summary": {"finding_count": self.finding_count, "error_count": len(self.errors)},
            "findings": [asdict(item) for item in self.findings],
            "errors": list(self.errors),
        }
