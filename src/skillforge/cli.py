"""Command-line interface."""

import argparse
import json
from .engine import scan_skill
from .parser import SkillParseError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skillforge", description="Inspect AI agent skills without executing them.")
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="Statically inspect a skill directory")
    scan.add_argument("path", help="Directory containing SKILL.md")
    scan.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = scan_skill(args.path)
    except SkillParseError as exc:
        print(f"SkillForge: {exc}")
        return 2

    if args.format == "json":
        print(json.dumps(report.to_dict(), indent=2))
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

    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
