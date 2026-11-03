"""Bounded, deterministic static checks for common risky patterns.

Skill contents are untrusted data. This module never imports or executes them.
The checks are heuristic indicators, not proof of malicious behaviour.
"""

import os
import re
import stat
from pathlib import Path

from .models import Finding

# Skill files are untrusted, so every pattern below must run in time linear in
# the line length. Avoid unbounded gaps between two variable-length parts and
# adjacent quantifiers over overlapping character classes: both backtrack
# quadratically (a 100 KB line once took ~10 s). tests/test_rules.py enforces this.

_SHELL = r"(?:(?:ba|z|da|k)?sh)"

# Interpreters that execute a script read from stdin. They only count when they
# read the program from the pipe (bare, or with a trailing `-`), so harmless
# data processing such as `curl ... | python3 -m json.tool` or
# `... | python -c "..."` is not flagged.
_STDIN_INTERPRETER = (
    r"(?:python[0-9]*(?:\.[0-9]+)?|node|perl|ruby)"
    r"(?=\s*(?:$|[;&|)]|-(?:\s|$)))"
)

# Command substitution that runs downloaded text: eval "$(curl ...)",
# eval `curl ...`, bash -c "$(curl ...)".
_RUN_DOWNLOAD = (
    r"\b(?:eval|" + _SHELL + r"\s+-c)\s+[\"']?(?:\$\(|`)\s*(?:curl|wget)\b"
)

# Broad deletion targets: the filesystem root, a top-level system directory, or
# the home directory itself (optionally quoted, with an optional trailing /*).
_BROAD_TARGET = (
    r"""["']?(?:"""
    r"""/(?:(?:bin|boot|dev|etc|home|lib|lib32|lib64|opt|proc|root|sbin|srv|sys|usr|var"""
    r"""|Users|System|Library|Applications)/?)?"""
    r"""|~/?|\$\{?HOME\}?/?"""
    r""")\*?["']?(?=\s|$|[;&|])"""
)

RULES = [
    (
        "SF001", "Download piped to shell", "critical",
        re.compile(
            # curl|wget ... | [sudo [-flags]] [/bin/]sh   (up to 200 characters between)
            r"\b(?:curl|wget)\b[^\n]{0,200}?\|\s*(?:sudo\s+(?:-\S+\s+)*)?(?:/(?:usr/)?(?:local/)?bin/)?"
            r"(?:" + _SHELL + r"\b|" + _STDIN_INTERPRETER + r")"
            # sh <(curl ...)
            r"|\b" + _SHELL + r"\s+<\(\s*(?:curl|wget)\b"
            # eval "$(curl ...)" and bash -c "$(curl ...)"
            r"|" + _RUN_DOWNLOAD,
            re.IGNORECASE,
        ),
        "Downloads content and pipes it directly into a shell interpreter.",
    ),
    (
        "SF002", "Recursive deletion of broad target", "high",
        re.compile(
            # rm with a recursive flag (-r, -R, -rf, -fr, --recursive, ...) aimed at a broad target.
            # The lookahead finds the flag; the options are then consumed once, in a single pass.
            r"\brm(?=(?:\s+-\S*)*?\s+(?:-(?=[A-Za-z]*[rR])[A-Za-z]+|--recursive)(?=\s))"
            r"(?:\s+-\S*)*\s+" + _BROAD_TARGET,
            re.IGNORECASE,
        ),
        "Contains a recursive delete command targeting a broad location.",
    ),
    (
        "SF003", "Credential path reference", "medium",
        re.compile(
            r"\.ssh(?:/|\b)|\.aws/credentials|\.config/gcloud|\.npmrc|\.netrc|\.gnupg|\.kube/config"
            r"|\.docker/config\.json|\bid_(?:rsa|dsa|ecdsa|ed25519)\b",
            re.IGNORECASE,
        ),
        "References a common credential or private-key location.",
    ),
    (
        "SF004", "Environment access", "low",
        re.compile(
            r"\bprintenv\b|os\.environ|os\.getenv|process\.env|(?-i:\bENV(?:\[|\{|\.fetch\b))"
            # `env` only when used as a command (dumping the environment), not as part of
            # `#!/usr/bin/env python`, `.env`, or the word "env" in prose.
            r"|(?:^|[;&|`(])\s*(?:\$\s+)?env\s*(?=$|[|;&>)`])",
            re.IGNORECASE,
        ),
        "May read environment variables, which can contain secrets.",
    ),
    (
        "SF005", "Instruction override language", "medium",
        re.compile(
            r"\b(?:ignore|override|disregard|forget)\s+(?:(?:all|any|your|the|these|those)\s+){0,2}"
            r"(?:previous|prior|above|earlier|system)\s+instructions",
            re.IGNORECASE,
        ),
        "Contains language that may attempt to override higher-priority instructions.",
    ),
]

TEXT_SUFFIXES = {".md", ".txt", ".py", ".sh", ".bash", ".zsh", ".js", ".ts", ".json", ".yaml", ".yml", ".toml"}
IGNORED_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}
MAX_FILE_BYTES = 1_000_000
MAX_ENTRIES = 10_000

# Evidence is the matched text only (never the whole line) and is capped so a
# finding stays small even when a rule matches a long span. It is untrusted
# skill content: escape it before showing it anywhere.
MAX_EVIDENCE_CHARS = 240

# Findings link to the matching section of the rule reference. The path is
# relative to the repository root so reports stay portable.
RULE_REFERENCE_BASE = "docs/RULES.md"

# Qualitative confidence that the pattern matched as intended, not a probability
# that a skill is malicious. Keep in sync with docs/RULES.md; every rule in
# RULES needs an entry (tests/test_rules.py enforces this).
RULE_CONFIDENCE = {
    "SF001": "high",
    "SF002": "high",
    "SF003": "medium",
    "SF004": "low",
    "SF005": "medium",
}


def _read_text_limited(path: Path) -> tuple[str | None, str | None]:
    """Read at most MAX_FILE_BYTES + 1 bytes and reject non-regular files."""
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    # Prevent following a symlink on platforms that support O_NOFOLLOW.
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = None
    try:
        descriptor = os.open(path, flags)
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            return None, "not a regular file"
        if info.st_size > MAX_FILE_BYTES:
            return None, f"file exceeds {MAX_FILE_BYTES} byte limit"
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = None  # fdopen now owns the descriptor
            raw = stream.read(MAX_FILE_BYTES + 1)
        if len(raw) > MAX_FILE_BYTES:
            return None, f"file exceeds {MAX_FILE_BYTES} byte limit"
        return raw.decode("utf-8"), None
    except UnicodeDecodeError:
        return None, "file is not valid UTF-8 text"
    except OSError as exc:
        return None, str(exc)
    finally:
        if descriptor is not None:
            os.close(descriptor)


def scan_files(skill_dir: str | Path) -> tuple[list[Finding], list[str]]:
    """Inspect supported text files below a skill directory.

    Traversal and findings are sorted for repeatable output. Common generated
    directories and symlinks are skipped. Total filesystem entries and each
    file's bytes are bounded.
    """
    root = Path(skill_dir).expanduser().resolve()
    findings: list[Finding] = []
    errors: list[str] = []

    if not root.exists() or not root.is_dir():
        return findings, ["Skill directory is unavailable or is not a directory."]

    entries_seen = 0
    def record_walk_error(exc: OSError) -> None:
        errors.append("Could not traverse a directory: " + (exc.strerror or "filesystem error"))

    for current, directories, filenames in os.walk(root, topdown=True, followlinks=False, onerror=record_walk_error):
        current_path = Path(current)
        entries_seen += len(directories) + len(filenames)
        if entries_seen > MAX_ENTRIES:
            errors.append(f"Entry limit reached ({MAX_ENTRIES}); remaining files were not scanned.")
            break

        kept_directories = []
        for dirname in sorted(directories):
            child = current_path / dirname
            if dirname in IGNORED_DIRS or child.is_symlink():
                continue
            kept_directories.append(dirname)
        directories[:] = kept_directories

        for filename in sorted(filenames):
            path = current_path / filename
            if path.is_symlink() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue

            content, error = _read_text_limited(path)
            relative = path.relative_to(root).as_posix()
            if error:
                errors.append(f"Skipped {relative}: {error}")
                continue

            for line_number, line in enumerate((content or "").splitlines(), start=1):
                for rule_id, title, severity, pattern, message in RULES:
                    match = pattern.search(line)
                    if match:
                        evidence = match.group(0).strip()
                        if len(evidence) > MAX_EVIDENCE_CHARS:
                            evidence = evidence[: MAX_EVIDENCE_CHARS - 1] + "…"
                        findings.append(Finding(
                            rule_id=rule_id,
                            title=title,
                            severity=severity,
                            confidence=RULE_CONFIDENCE[rule_id],
                            message=message,
                            evidence=evidence,
                            rule_reference=f"{RULE_REFERENCE_BASE}#rule-{rule_id.lower()}",
                            file_path=relative,
                            line=line_number,
                        ))
    findings.sort(key=lambda item: (item.file_path, item.line, item.rule_id))
    return findings, errors
