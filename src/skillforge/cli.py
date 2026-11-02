"""Command-line interface."""

import argparse
import json
import sys

from . import __version__
from .engine import scan_skill
from .parser import SkillParseError

SEVERITY_ORDER = {"low": 1, "medium": 2, "high": 3, "critical": 4}


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
        print(f"Skill: {report.skill.name}")
        print(f"Description: {report.skill.description}")
        print(f"Scanner: {report.scanner_version}")
        print(f"Findings: {report.finding_count}")
        for finding in report.findings:
            print(f"[{finding.severity.upper()}] {finding.rule_id} {finding.file_path}:{finding.line} — {finding.title}")
            print(f"  {finding.message}")
        for error in report.errors:
            print(f"[WARNING] {error}")
        if not report.findings:
            print("No heuristic findings. This is not a guarantee of safety.")

    if report.errors:
        return 2
    if args.fail_on != "none":
        threshold = SEVERITY_ORDER[args.fail_on]
        if any(SEVERITY_ORDER[item.severity] >= threshold for item in report.findings):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
