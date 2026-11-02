import re
from pathlib import Path

import skillforge

CHANGELOG = Path(__file__).resolve().parent.parent / "CHANGELOG.md"


def test_version_matches_latest_released_changelog_entry():
    # `__version__` once lagged behind the changelog and pyproject (0.1.0 vs 0.1.1),
    # so `skillforge --version` and every report advertised a stale version.
    released = re.findall(r"^## (\d+\.\d+\.\d+)\b", CHANGELOG.read_text(encoding="utf-8"), re.MULTILINE)
    assert released, "CHANGELOG.md has no released version heading"
    assert skillforge.__version__ == released[0]


def test_cli_reports_package_version(capsys):
    import pytest

    from skillforge import cli

    with pytest.raises(SystemExit) as exit_info:
        cli.build_parser().parse_args(["--version"])
    assert exit_info.value.code == 0
    assert skillforge.__version__ in capsys.readouterr().out
