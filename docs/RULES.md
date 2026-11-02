# Scanner rules

Rules are heuristic signals for manual review. They are not a malware verdict.

| ID | Severity | Current signal | Important limitation |
|---|---|---|---|
| SF001 | Critical | `curl` or `wget` piped into a shell (`sh`, `bash`, `zsh`, `dash`, `ksh`, optionally via `sudo` or `/bin/`), or `sh <(curl ...)` | Does not detect every download-and-execute technique, such as piping into `python` or a download saved to disk and run later |
| SF002 | High | `rm` with a recursive flag (`-r`, `-R`, `-rf`, `--recursive`, ...) targeting `/`, a top-level system directory, or the home directory itself | Only a broad *target* is flagged, so `rm -rf /tmp/build` is not. Shell syntax and quoting variants may evade the pattern |
| SF003 | Medium | References to common SSH, AWS, Google Cloud, or npm credential paths | A path reference may be documentation or a legitimate operation. Other credential stores (`.kube/config`, `.netrc`, `.gnupg`, ...) are not covered yet |
| SF004 | Low | Environment-variable access: `os.environ`, `os.getenv`, `process.env`, `ENV[...]`, `printenv`, or `env` used as a command | Environment access is often legitimate. `env` inside a shebang, `.env` file names, or prose is not flagged |
| SF005 | Medium | Phrases that resemble attempts to override prior/system instructions (for example "ignore your previous instructions") | Context matters; legitimate defensive instructions can match |

## Rule quality requirements

Every new rule should include:
- A stable identifier that is never silently reused.
- A concise explanation of the evidence being detected.
- At least one positive fixture and one benign negative fixture.
- A documented severity rationale.
- Known bypasses and false-positive limitations.
- A pattern that runs in linear time. Skill files are untrusted, so avoid unbounded gaps between two variable-length parts and adjacent quantifiers over overlapping character classes. `tests/test_rules.py` runs every rule against adversarial long lines.

A finding means “review this evidence,” not “this skill is malicious.” Rule matches are currently line-based and may miss multi-line or obfuscated behaviour.
