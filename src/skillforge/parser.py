"""Minimal, dependency-free SKILL.md frontmatter parser.

This intentionally supports a small YAML-like subset. It is not a general YAML
parser; unsupported or malformed metadata is reported clearly.
"""

from pathlib import Path
from .models import SkillMetadata


class SkillParseError(ValueError):
    """Raised when a skill entry point cannot be parsed."""


def parse_skill(skill_dir: str | Path) -> tuple[SkillMetadata, Path]:
    root = Path(skill_dir).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SkillParseError(f"Skill directory does not exist: {root}")

    skill_file = root / "SKILL.md"
    if not skill_file.is_file():
        raise SkillParseError(f"Missing SKILL.md in: {root}")

    try:
        content = skill_file.read_text(encoding="utf-8")
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
    for number, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise SkillParseError(f"Invalid frontmatter at line {number}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key not in {"name", "description"}:
            continue
        if not key or not value:
            raise SkillParseError(f"Missing value for {key or 'metadata field'} at line {number}")
        metadata[key] = value

    missing = {"name", "description"} - metadata.keys()
    if missing:
        raise SkillParseError(f"Missing required metadata: {', '.join(sorted(missing))}")

    return SkillMetadata(
        name=metadata["name"],
        description=metadata["description"],
        path=str(root),
    ), skill_file
