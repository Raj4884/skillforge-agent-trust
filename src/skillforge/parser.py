"""Small dependency-free parser for SKILL.md YAML frontmatter.

This is intentionally not a complete YAML implementation. It supports the
required name/description fields, plain and quoted scalars (including values
that continue on following lines), comments, and folded/literal block scalars.
In double-quoted strings only the ``\\"`` and ``\\\\`` escapes are interpreted;
other backslash sequences are kept as written. Unsupported YAML features should
be handled explicitly.

Skill files are untrusted input, so every helper here runs in linear time.
"""

import re
import textwrap
from pathlib import Path

from .models import SkillMetadata

MAX_METADATA_BYTES = 256_000
REQUIRED_KEYS = {"name", "description"}

_KEY_PATTERN = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$")
_BLOCK_HEADER = re.compile(r"[>|](?:[+-]?[0-9]?|[0-9][+-])")


class SkillParseError(ValueError):
    """Raised when a skill entry point cannot be parsed."""


def _strip_comment(value: str) -> str:
    """Remove a YAML comment (a ``#`` at the start or after whitespace).

    Hashes inside URLs or words are preserved. A character scan is used instead
    of a regular expression so that long whitespace runs cannot cause
    quadratic backtracking.
    """
    for position, char in enumerate(value):
        if char == "#" and (position == 0 or value[position - 1].isspace()):
            return value[:position].rstrip()
    return value.rstrip()


def _scan_quoted(text: str) -> tuple[str, str] | None:
    """Return ``(decoded_value, remainder)`` or ``None`` if the quote is unclosed."""
    quote = text[0]
    decoded: list[str] = []
    index = 1
    while index < len(text):
        char = text[index]
        if quote == "'" and char == "'":
            if text[index + 1:index + 2] == "'":  # '' is an escaped single quote
                decoded.append("'")
                index += 2
                continue
            return "".join(decoded), text[index + 1:]
        if quote == '"':
            if char == "\\" and text[index + 1:index + 2] in {'"', "\\"}:
                decoded.append(text[index + 1])
                index += 2
                continue
            if char == '"':
                return "".join(decoded), text[index + 1:]
        decoded.append(char)
        index += 1
    return None


def _read_quoted(first: str, lines: list[str], index: int, end: int, line_number: int) -> tuple[str, int]:
    """Read a quoted scalar that may continue on following lines."""
    buffer = first
    while True:
        scanned = _scan_quoted(buffer)
        if scanned is not None:
            break
        if index >= end:
            raise SkillParseError(f"Unclosed quoted value at line {line_number}")
        continuation = lines[index].strip()
        index += 1
        if continuation:
            buffer += " " + continuation

    value, rest = scanned
    trailing = rest.strip()
    # Only whitespace or a comment (separated by whitespace) may follow the closing quote.
    if trailing and not (rest[:1].isspace() and trailing.startswith("#")):
        raise SkillParseError(f"Unexpected text after quoted value at line {line_number}")
    return value, index


def _read_plain(first: str, lines: list[str], index: int, end: int) -> tuple[str, int]:
    """Read a plain scalar, folding any indented continuation lines into it."""
    parts = [_strip_comment(first.strip())]
    while index < end:
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if not line[:1].isspace() or line.lstrip().startswith("#"):
            break
        parts.append(_strip_comment(line.strip()))
        index += 1
    return " ".join(part for part in parts if part), index


def _read_block(header: str, lines: list[str], index: int, end: int) -> tuple[str, int]:
    """Read a folded (``>``) or literal (``|``) block scalar."""
    block_lines = []
    while index < end and (not lines[index].strip() or lines[index][:1].isspace()):
        block_lines.append(lines[index])
        index += 1
    block = textwrap.dedent("\n".join(block_lines)).strip()
    if header.startswith(">"):
        block = " ".join(part.strip() for part in block.splitlines())
    return block, index


def parse_skill(skill_dir: str | Path) -> tuple[SkillMetadata, Path]:
    root = Path(skill_dir).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SkillParseError(f"Skill directory does not exist: {root}")

    skill_file = root / "SKILL.md"
    if not skill_file.is_file() or skill_file.is_symlink():
        raise SkillParseError(f"Missing regular SKILL.md file in: {root}")

    try:
        with skill_file.open("rb") as stream:
            raw = stream.read(MAX_METADATA_BYTES + 1)
        if len(raw) > MAX_METADATA_BYTES:
            raise SkillParseError(f"SKILL.md exceeds {MAX_METADATA_BYTES} byte limit")
        # utf-8-sig tolerates the byte-order mark that some Windows editors add.
        content = raw.decode("utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise SkillParseError(f"Could not read SKILL.md: {exc}") from exc

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        raise SkillParseError("SKILL.md must start with YAML frontmatter (---)")

    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise SkillParseError("Unclosed YAML frontmatter") from exc

    metadata: dict[str, str] = {}
    index = 1
    while index < end:
        line = lines[index]
        number = index + 1
        index += 1
        if not line.strip() or line.lstrip().startswith("#") or line[:1].isspace():
            continue

        match = _KEY_PATTERN.match(line)
        if not match:
            continue
        key, raw_value = match.groups()
        if key not in REQUIRED_KEYS:
            continue
        if key in metadata:
            raise SkillParseError(f"Duplicate {key!r} field at line {number}")

        value = raw_value.strip()
        header = _strip_comment(value)
        if _BLOCK_HEADER.fullmatch(header):
            value, index = _read_block(header, lines, index, end)
        elif value[:1] in {"'", '"'}:
            value, index = _read_quoted(value, lines, index, end, number)
        else:
            value, index = _read_plain(value, lines, index, end)

        if not value:
            raise SkillParseError(f"Missing value for {key!r} at line {number}")
        metadata[key] = value

    missing = REQUIRED_KEYS - metadata.keys()
    if missing:
        raise SkillParseError(f"Missing required metadata: {', '.join(sorted(missing))}")

    return SkillMetadata(
        name=metadata["name"],
        description=metadata["description"],
        # A relative marker keeps reports portable across different machines.
        path=".",
    ), skill_file
