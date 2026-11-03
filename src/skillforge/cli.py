"""Command-line interface."""

import argparse
import json
import sys

from . import __version__
from .engine import scan_skill
from .parser import SkillParseError

SEVERITY_ORDER = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def _display(text: str) -> str:
    """Escape control and invisible-format characters in untrusted text.

    Skill names, descriptions and file names come from the skill under review.
    Printed raw, ANSI escape sequences, newlines or bidirectional overrides could
    rewrite or hide the scanner's own output (for example erase the findings).
    JSON output is already escaped by ``json.dumps``.
    """
    return "".join(char if char.isprintable() else char.encode("unicode_escape").decode("ascii") for char in text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skillforge", description="Inspect AI agent skills without executing them.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="Statically inspect a skill directory")
    scan.add_argument("path", help="Directory containing SKILL.md")
    scan.add_argument("--format", choices=("text", "json"), default="text")
    scan.add_argument(
        "--fail-on",
        choices=("none", "low", "medium", "high", "critical"),
        default="none",
        help="Return exit code 1 when a finding at or above this severity is present.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = scan_skill(args.path)
    except SkillParseError as exc:
        print(f"SkillForge: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(f"Skill: {_display(report.skill.name)}")
        print(f"Description: {_display(report.skill.description)}")
        print(f"Scanner: {report.scanner_version}")
        print(f"Findings: {report.finding_count}")
        for finding in report.findings:
            location = f"{_display(finding.file_path)}:{finding.line}"
            print(f"[{finding.severity.upper()}] {finding.rule_id} {location} ({finding.confidence} confidence) — {finding.title}")
            print(f"  Evidence: {_display(finding.evidence)}")
            print(f"  Why: {_display(finding.message)}")
            print(f"  Rule: {finding.rule_reference}")
        for error in report.errors:
            print(f"[WARNING] {_display(error)}")
        if not report.findings:
            print("No heuristic findings. This is not a guarantee of safety.")

    # A finding at or above the threshold is a policy failure and must not be
    # hidden by an unrelated scan warning (such as one skipped file), so it is
    # checked first. Scan errors only decide the exit code when the policy passes.
    if args.fail_on != "none":
        threshold = SEVERITY_ORDER[args.fail_on]
        if any(SEVERITY_ORDER[item.severity] >= threshold for item in report.findings):
            return 1
    if report.errors:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
