"""Heuristic static checks for common risky patterns.

The scanner reads text files only. It never imports or executes skill content.
"""

import re
from pathlib import Path
from .models import Finding

RULES = [
    (
        "SF001", "Download piped to shell", "critical",
        re.compile(r"\b(?:curl|wget)\b[^\n|]*\|\s*(?:ba)?sh\b", re.IGNORECASE),
        "Downloads content and pipes it directly into a shell interpreter.",
    ),
    (
        "SF002", "Recursive force deletion", "high",
        re.compile(r"\brm\s+-[^\n]*r[^\n]*f[^\n]*\s+(?:/|\$HOME|~)", re.IGNORECASE),
        "Contains a recursive force-delete command targeting a broad location.",
    ),
    (
        "SF003", "Credential path reference", "medium",
        re.compile(r"(?:\.ssh/|\.aws/credentials|\.config/gcloud|id_rsa|\.npmrc)", re.IGNORECASE),
        "References a common credential or private-key location.",
    ),
    (
        "SF004", "Environment access", "low",
        re.compile(r"\b(?:printenv|env)\b|os\.environ|process\.env", re.IGNORECASE),
        "Reads environment variables, which may contain secrets.",
    ),
    (
        "SF005", "Instruction override language", "medium",
        re.compile(r"(?:ignore|override|disregard)\s+(?:all\s+)?(?:previous|prior|system)\s+instructions", re.IGNORECASE),
        "Contains language that may attempt to override higher-priority instructions.",
    ),
]

TEXT_SUFFIXES = {".md", ".txt", ".py", ".sh", ".js", ".ts", ".json", ".yaml", ".yml", ".toml"}
MAX_FILE_BYTES = 1_000_000
MAX_FILES = 2_000


def scan_files(skill_dir: str | Path) -> tuple[list[Finding], list[str]]:
    root = Path(skill_dir).expanduser().resolve()
    findings: list[Finding] = []
    errors: list[str] = []
    files_seen = 0

    # Do not follow directory symlinks; skip symlinked files as well.
    for path in root.rglob("*"):
        try:
            if path.is_symlink() or not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            files_seen += 1
            if files_seen > MAX_FILES:
                errors.append(f"File limit reached ({MAX_FILES}); remaining files were not scanned.")
                break
            if path.stat().st_size > MAX_FILE_BYTES:
                errors.append(f"Skipped oversized file: {path.relative_to(root)}")
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"Could not inspect {path}: {exc}")
            continue

        relative = str(path.relative_to(root))
        for line_number, line in enumerate(text.splitlines(), start=1):
            for rule_id, title, severity, pattern, message in RULES:
                if pattern.search(line):
                    findings.append(Finding(
                        rule_id=rule_id,
                        title=title,
                        severity=severity,
                        message=message,
                        file_path=relative,
                        line=line_number,
                    ))

    return findings, errors
