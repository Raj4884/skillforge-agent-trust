# Changelog

## 0.2.0 — Reliable evidence engine (2026-11-03)

Findings now explain themselves: each one carries the matched text, a confidence level and a link to its rule. The JSON report is versioned, the scanner resists hostile input, and a fixture corpus measures its accuracy.

**Upgrade notes:** the JSON report gains fields (additive). `--fail-on` now exits 1 when a finding meets the threshold even if a file was skipped (previously 2). SF002 was renamed to "Recursive deletion of broad target".

### Added

- Findings now carry the matched `evidence` (the matching text only, capped at 240 characters), a qualitative `confidence` (`low`, `medium` or `high`) and a `rule_reference` link to the rule's section in `docs/RULES.md`.
- JSON reports include a `schema_version` field (currently `1.0`). The text report shows evidence, confidence and the rule reference for every finding.
- CI runs Ruff and builds and smoke-tests the wheel.
- Tests keep `docs/RULES.md` (titles, severities, confidence, anchors) in sync with the scanner rules.
- A fixture corpus of 23 inert skills (`tests/corpus/`): malicious, benign, known gaps and known false positives. A regression test pins the scanner's behavior on each, and `docs/EVALUATION.md` reports per-rule recall and precision. `python tests/corpus_report.py --write` regenerates the page and a test fails if it is stale.

### Changed

- **Behavior change:** `--fail-on` now exits with 1 whenever a finding meets the threshold, even if some files were skipped or could not be read. Previously any scan error returned 2 first, so a critical finding could be reported as a mere warning in CI. Scan errors still return 2 when no finding meets the threshold. The README documents all exit codes.
- SF001 now also flags `eval "$(curl ...)"` and `bash -c "$(curl ...)"` (the common one-line installer form), and `curl ... | python3`, `node`, `perl` or `ruby` when the interpreter reads the program from the pipe. `curl ... | python3 -m json.tool` and `python -c "..."` are not flagged.
- SF003 now covers `.netrc`, `.gnupg`, `.kube/config`, `.docker/config.json` and `id_dsa`, `id_ecdsa`, `id_ed25519` keys. Key names now match as whole words, so `id_rsa_note` no longer matches.
- SF002 is now titled "Recursive deletion of broad target" to match what it detects (a recursive delete aimed at `/`, a top-level system directory or the home directory, with or without `-f`).
- Error messages no longer include absolute local paths.

### Security

- Fixed quadratic regex backtracking in SF001, SF002 and the parser's comment stripping. A hostile skill could stall a scan for minutes (SF001 took about 10 s on a 100 KB line). Every rule is now linear-time and covered by timing tests.
- Text output now escapes control and invisible-format characters in skill names, descriptions and file paths, so a skill can no longer rewrite or hide scanner output with ANSI escape sequences or bidirectional overrides.

### Fixed

- `skillforge --version` and reports advertised 0.1.0 while the package was 0.1.1. The version now has a single source (`skillforge.__version__`, read by `pyproject.toml`) and a test keeps it aligned with this changelog.
- Parser accepts a UTF-8 byte-order mark.
- Parser accepts a trailing `# comment` after a quoted value, unescapes `''` in single-quoted values, and handles `\"` and `\\` in double-quoted values.
- Parser no longer truncates a plain description that continues on following lines, and supports values that start on the next line, multi-line quoted values, and block scalars for `name`.
- SF002 no longer flags `rm -f /tmp/file` or `rm -rf /tmp/build`; it now flags recursive deletion of broad targets only, and also catches `rm -r -f /`, `rm --recursive --force /`, `"$HOME"` and `${HOME}`.
- SF004 no longer flags `#!/usr/bin/env python`, `.env` or the word "env" in prose; it now also detects `os.getenv` and Ruby `ENV[...]`.
- SF001 now detects `| sudo bash`, `| /bin/sh`, multi-stage pipelines and `sh <(curl ...)`.
- SF005 now detects phrasing such as "ignore your previous instructions" and "ignore the above instructions".

## 0.1.1 — Reliability and test improvements

- Bound scanner reads to a maximum number of bytes per file.
- Added traversal entry limits, symlink skipping, and generated-directory exclusions.
- Made finding order deterministic and report paths portable.
- Added folded/literal multiline descriptions and duplicate metadata checks.
- Added CLI `--version` and `--fail-on` severity threshold.
- Expanded tests and added a Python 3.10–3.13 CI matrix.
- Added scanner rule reference and security policy.

## 0.1.0 — Initial prototype

- Added SKILL.md metadata parsing.
- Added five heuristic static inspection rules.
- Added text and JSON CLI output.
- Added unit tests and GitHub Actions CI.
- Documented initial product scope and threat model.
