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


def test_utf8_bom_is_accepted(tmp_path: Path):
    (tmp_path / "SKILL.md").write_bytes(b"\xef\xbb\xbf---\nname: demo\ndescription: With a BOM\n---\n")
    metadata, _ = parse_skill(tmp_path)
    assert metadata.name == "demo"
    assert metadata.description == "With a BOM"


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ('description: "Quoted value" # trailing comment', "Quoted value"),
        ("description: 'Single quoted' # trailing comment", "Single quoted"),
        ("description: 'It''s escaped'", "It's escaped"),
        (r'description: "Says \"hi\" and C:\\temp"', 'Says "hi" and C:\\temp'),
        ("description: Plain value # comment", "Plain value"),
        ("description: http://example.invalid/page#anchor", "http://example.invalid/page#anchor"),
    ],
)
def test_scalar_forms(tmp_path: Path, line: str, expected: str):
    write_skill(tmp_path, f"---\nname: demo\n{line}\n---")
    metadata, _ = parse_skill(tmp_path)
    assert metadata.description == expected


def test_plain_multiline_description_is_not_truncated(tmp_path: Path):
    write_skill(tmp_path, "---\nname: demo\ndescription: First part\n  second part\n  third part\n---")
    metadata, _ = parse_skill(tmp_path)
    assert metadata.description == "First part second part third part"


def test_description_on_following_indented_line(tmp_path: Path):
    write_skill(tmp_path, "---\nname: demo\ndescription:\n  Starts on the next line\n---")
    metadata, _ = parse_skill(tmp_path)
    assert metadata.description == "Starts on the next line"


def test_quoted_multiline_description(tmp_path: Path):
    write_skill(tmp_path, '---\nname: demo\ndescription: "First part\n  second part"\n---')
    metadata, _ = parse_skill(tmp_path)
    assert metadata.description == "First part second part"


def test_block_scalar_works_for_name_too(tmp_path: Path):
    write_skill(tmp_path, "---\nname: >\n  folded name\ndescription: Example\n---")
    metadata, _ = parse_skill(tmp_path)
    assert metadata.name == "folded name"


def test_indented_children_of_other_keys_are_ignored(tmp_path: Path):
    write_skill(tmp_path, "---\nname: demo\nmetadata:\n  name: nested\n  version: 1\ndescription: Example\n---")
    metadata, _ = parse_skill(tmp_path)
    assert (metadata.name, metadata.description) == ("demo", "Example")


@pytest.mark.parametrize(
    ("line", "message"),
    [
        ('description: "never closed', "Unclosed"),
        ('description: "closed" trailing text', "Unexpected text"),
        ("description:", "Missing value"),
    ],
)
def test_malformed_values_are_rejected(tmp_path: Path, line: str, message: str):
    write_skill(tmp_path, f"---\nname: demo\n{line}\n---")
    with pytest.raises(SkillParseError, match=message):
        parse_skill(tmp_path)


def test_long_whitespace_run_in_value_is_parsed_quickly(tmp_path: Path):
    # The old comment-stripping regex backtracked quadratically on inputs like this.
    import time

    write_skill(tmp_path, "---\nname: demo\ndescription: a" + " " * 100_000 + "b\n---")
    started = time.perf_counter()
    metadata, _ = parse_skill(tmp_path)
    assert time.perf_counter() - started < 2.0
    assert metadata.description.startswith("a") and metadata.description.endswith("b")
