from pathlib import Path

import pytest

from skillforge.parser import SkillParseError, parse_skill


def write_skill(folder: Path, frontmatter: str) -> None:
    (folder / "SKILL.md").write_text(frontmatter + "\n# Instructions\n", encoding="utf-8")


def test_parse_valid_skill(tmp_path: Path):
    write_skill(tmp_path, '---\nname: demo\ndescription: A demo skill\n---')
    metadata, file_path = parse_skill(tmp_path)
    assert metadata.name == "demo"
    assert metadata.description == "A demo skill"
    assert metadata.path == "."
    assert file_path.name == "SKILL.md"


def test_missing_frontmatter_is_rejected(tmp_path: Path):
    write_skill(tmp_path, "# No frontmatter")
    with pytest.raises(SkillParseError):
        parse_skill(tmp_path)


def test_quoted_description_with_colon_and_hash(tmp_path: Path):
    write_skill(tmp_path, '''---
name: demo
description: "A helper: use # safely"
---''')
    metadata, _ = parse_skill(tmp_path)
    assert metadata.description == "A helper: use # safely"


def test_folded_multiline_description(tmp_path: Path):
    write_skill(tmp_path, '''---
name: demo
description: >
  First line of the description
  continues on this line.
---''')
    metadata, _ = parse_skill(tmp_path)
    assert metadata.description == "First line of the description continues on this line."


def test_duplicate_required_field_is_rejected(tmp_path: Path):
    write_skill(tmp_path, '''---
name: first
name: second
description: Example
---''')
    with pytest.raises(SkillParseError, match="Duplicate"):
        parse_skill(tmp_path)


def test_oversized_skill_file_is_rejected(tmp_path: Path):
    (tmp_path / "SKILL.md").write_bytes(b"x" * 300_000)
    with pytest.raises(SkillParseError, match="exceeds"):
        parse_skill(tmp_path)
