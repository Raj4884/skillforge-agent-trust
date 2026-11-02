"""Scan orchestration."""

from pathlib import Path

from . import __version__
from .models import ScanReport
from .parser import parse_skill
from .scanner import scan_files


def scan_skill(skill_dir: str | Path) -> ScanReport:
    metadata, _ = parse_skill(skill_dir)
    findings, errors = scan_files(skill_dir)
    return ScanReport(
        scanner_version=__version__,
        skill=metadata,
        findings=findings,
        errors=errors,
    )
