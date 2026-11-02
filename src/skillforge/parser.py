"""Small dependency-free parser for SKILL.md YAML frontmatter.

This is intentionally not a complete YAML implementation. It supports the
required name/description fields, quoted scalars, comments, and folded/literal
block descriptions. Unsupported YAML features should be handled explicitly.
"""

import re
import textwrap
from pathlib import Path

from .models import SkillMetadata

MAX_METADATA_BYTES = 256_000


class SkillParseError(ValueError):
    """Raised when a skill entry point cannot be parsed."""


def _clean_scalar(value: str, line_number: int) -> str:
    value = value.strip()
    if not value:
        return ""
    if value[0] in {"'", '"'}:
        quote = value[0]
        if len(value) < 2 or value[-1] != quote:
            raise SkillParseError(f"Unclosed quoted value at line {line_number}")
        return value[1:-1].replace("\\" + quote, quote)
    # A YAML comment starts after whitespace; preserve hashes inside URLs/words.
    value = re.sub(r"\s+#.*$", "", value).strip()
    return value


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
        content = raw.decode("utf-8")
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

        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$", line)
        if not match:
            continue
        key, raw_value = match.groups()
        if key not in {"name", "description"}:
            continue
        if key in metadata:
            raise SkillParseError(f"Duplicate {key!r} field at line {number}")

        value = raw_value.strip()
        if key == "description" and value in {">", "|", ">-", "|-", ">+", "|+"}:
            block_lines = []
            while index < end and (not lines[index].strip() or lines[index][:1].isspace()):
                block_lines.append(lines[index])
                index += 1
            block = textwrap.dedent("\n".join(block_lines)).strip()
            value = " ".join(part.strip() for part in block.splitlines()) if value.startswith(">") else block
        else:
            value = _clean_scalar(value, number)

        if not value:
            raise SkillParseError(f"Missing value for {key!r} at line {number}")
        metadata[key] = value

    missing = {"name", "description"} - metadata.keys()
    if missing:
        raise SkillParseError(f"Missing required metadata: {', '.join(sorted(missing))}")

    return SkillMetadata(
        name=metadata["name"],
        description=metadata["description"],
        # A relative marker keeps reports portable across different machines.
        path=".",
    ), skill_file
