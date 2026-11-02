# Changelog

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
