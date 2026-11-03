import pytest
from corpus_report import CORPUS, DOC, fired_rules, load_manifest, render_markdown

from skillforge.scanner import RULES

MANIFEST = load_manifest()
RULE_IDS = {rule[0] for rule in RULES}


def test_manifest_matches_the_case_folders():
    on_disk = {path.name for path in (CORPUS / "cases").iterdir() if path.is_dir()}
    assert on_disk == {row["case"] for row in MANIFEST}
    assert len(MANIFEST) == len({row["case"] for row in MANIFEST}), "duplicate case names"


@pytest.mark.parametrize("row", MANIFEST, ids=[row["case"] for row in MANIFEST])
def test_scanner_behavior_matches_the_manifest(row):
    # A failure here means the scanner's behavior changed on a known skill. If the
    # change is an improvement, update `expected` (and the note) in the manifest
    # and regenerate docs/EVALUATION.md; if not, it is a regression.
    assert fired_rules(row["case"]) == set(row["expected"])


@pytest.mark.parametrize("row", MANIFEST, ids=[row["case"] for row in MANIFEST])
def test_manifest_rows_are_well_formed(row):
    assert row["label"] in {"malicious", "benign"}
    assert set(row["should"]) <= RULE_IDS and set(row["expected"]) <= RULE_IDS
    assert row["note"].strip()
    if row["label"] == "benign":
        assert row["should"] == [], "a benign skill should not expect any rule to fire"
    else:
        assert row["should"], "a malicious skill must name the rule(s) a reviewer wants"
    if row["expected"] != row["should"]:
        assert row["note"].startswith("KNOWN"), "gaps and false positives must be labelled in the note"


def test_every_rule_is_exercised_by_a_malicious_and_a_benign_case():
    for rule_id in RULE_IDS:
        assert any(rule_id in row["should"] for row in MANIFEST), f"{rule_id} has no malicious case"
    benign_with_no_findings = [row for row in MANIFEST if row["label"] == "benign" and not row["expected"]]
    assert len(benign_with_no_findings) >= 3


def test_evaluation_page_is_up_to_date():
    assert DOC.read_text(encoding="utf-8") == render_markdown(), (
        "docs/EVALUATION.md is stale: run `python tests/corpus_report.py --write`"
    )
