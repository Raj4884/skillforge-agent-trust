# Scanner rules

Rules are heuristic signals for manual review. They are not a malware verdict.

| ID | Severity | Current signal | Important limitation |
|---|---|---|---|
| SF001 | Critical | `curl` or `wget` piped into a shell interpreter | Does not detect every download-and-execute technique |
| SF002 | High | `rm` with recursive and force flags targeting a broad path | Shell syntax and quoting variants may evade the pattern |
| SF003 | Medium | References to common SSH, AWS, Google Cloud, or npm credential paths | A path reference may be documentation or a legitimate operation |
| SF004 | Low | Common environment-variable access patterns | Environment access is often legitimate |
| SF005 | Medium | Phrases that resemble attempts to override prior/system instructions | Context matters; legitimate defensive instructions can match |

## Rule quality requirements

Every new rule should include:
- A stable identifier that is never silently reused.
- A concise explanation of the evidence being detected.
- At least one positive fixture and one benign negative fixture.
- A documented severity rationale.
- Known bypasses and false-positive limitations.

A finding means “review this evidence,” not “this skill is malicious.” Rule matches are currently line-based and may miss multi-line or obfuscated behaviour.
