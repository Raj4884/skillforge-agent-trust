"""Bounded, deterministic static checks for common risky patterns.

Skill contents are untrusted data. This module never imports or executes them.
The checks are heuristic indicators, not proof of malicious behaviour.
"""

import os
import re
import stat
from pathlib import Path

from .models import Finding

RULES = [
    (
        "SF001", "Download piped to shell", "critical",
        re.compile(r"\b(?:curl|wget)\b[^\n|]*\|\s*(?:(?:ba)?sh|zsh)\b", re.IGNORECASE),
        "Downloads content and pipes it directly into a shell interpreter.",
    ),
    (
        "SF002", "Recursive force deletion", "high",
        re.compile(r"\brm\s+-[a-zA-Z]*[rf][a-zA-Z]*\s+(?:/|\$HOME\b|~(?:/|\s|$))", re.IGNORECASE),
        "Contains a recursive force-delete command targeting a broad location.",
    ),
    (
        "SF003", "Credential path reference", "medium",
        re.compile(r"(?:\.ssh(?:/|\b)|\.aws/credentials|\.config/gcloud|id_rsa|\.npmrc)", re.IGNORECASE),
        "References a common credential or private-key location.",
    ),
    (
        "SF004", "Environment access", "low",
        re.compile(r"\b(?:printenv|env)\b|os\.environ|process\.env", re.IGNORECASE),
        "May read environment variables, which can contain secrets.",
    ),
    (
        "SF005", "Instruction override language", "medium",
        re.compile(r"(?:ignore|override|disregard)\s+(?:all\s+)?(?:previous|prior|system)\s+instructions", re.IGNORECASE),
        "Contains language that may attempt to override higher-priority instructions.",
    ),
]

TEXT_SUFFIXES = {".md", ".txt", ".py", ".sh", ".bash", ".zsh", ".js", ".ts", ".json", ".yaml", ".yml", ".toml"}
IGNORED_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}
MAX_FILE_BYTES = 1_000_000
MAX_ENTRIES = 10_000


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
        return findings, [f"Skill directory does not exist or is not a directory: {root}"]

    entries_seen = 0
    stop = False

    def record_walk_error(exc: OSError) -> None:
        errors.append(f"Could not traverse {exc.filename or root}: {exc}")

    for current, directories, filenames in os.walk(root, topdown=True, followlinks=False, onerror=record_walk_error):
        current_path = Path(current)
        kept_directories = []
        for dirname in sorted(directories):
            child = current_path / dirname
            if dirname in IGNORED_DIRS or child.is_symlink():
                continue
            kept_directories.append(dirname)
        directories[:] = kept_directories

        for filename in sorted(filenames):
            entries_seen += 1
            if entries_seen > MAX_ENTRIES:
                errors.append(f"Entry limit reached ({MAX_ENTRIES}); remaining files were not scanned.")
                stop = True
                break

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
                    if pattern.search(line):
                        findings.append(Finding(
                            rule_id=rule_id,
                            title=title,
                            severity=severity,
                            message=message,
                            file_path=relative,
                            line=line_number,
                        ))
        if stop:
            break

    findings.sort(key=lambda item: (item.file_path, item.line, item.rule_id))
    return findings, errors
