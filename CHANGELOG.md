# Changelog

## Unreleased

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
