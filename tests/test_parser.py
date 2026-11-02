from pathlib import Path
import pytest

from skillforge.parser import SkillParseError, parse_skill


def test_parse_valid_skill(tmp_path: Path):
    (tmp_path / "SKILL.md").write_text(
        '---\nname: demo\ndescription: A demo skill\n---\n# Instructions\n',
        encoding="utf-8",
    )
    metadata, file_path = parse_skill(tmp_path)
    assert metadata.name == "demo"
    assert metadata.description == "A demo skill"
    assert file_path.name == "SKILL.md"


def test_missing_frontmatter_is_rejected(tmp_path: Path):
    (tmp_path / "SKILL.md").write_text("# No frontmatter\n", encoding="utf-8")
    with pytest.raises(SkillParseError):
        parse_skill(tmp_path)
