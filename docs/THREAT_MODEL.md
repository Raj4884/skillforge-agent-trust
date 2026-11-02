# Threat model

## Scope

SkillForge v0.1.x statically inspects local files that describe AI agent skills. It does not execute skill scripts or instructions.

## Assets to protect

- The developer's workstation and local files.
- Credentials available to the developer's environment.
- Integrity of the scan report.
- Confidentiality of skill source content.

## Trust boundaries

All skill content is untrusted input. A filename, metadata field, markdown instruction, script, or embedded snippet must be treated as data—not as instructions to SkillForge or its operator.

## Current safeguards

- No skill code is imported or executed.
- SKILL.md metadata reads are bounded to 256 KB.
- Scanner reads are bounded to 1 MB per file and 10,000 filesystem entries per scan.
- Scanner reads a restricted set of text file extensions.
- Symlinked files and directories are skipped; common generated directories are excluded.
- Findings are sorted by relative path, line, and rule ID.
- Findings explain the pattern observed; they do not claim malicious intent.

## Limitations

- Static pattern matching cannot understand all program semantics.
- Obfuscated, generated, encoded, indirect, or multi-line behaviour may not be detected.
- Harmless examples may trigger false positives.
- The scanner does not inspect every file format.
- Filesystem protections are best-effort across operating systems; concurrent filesystem changes and platform differences remain relevant.
- A clean report is not a certification or safety guarantee.

## Future dynamic evaluation

Dynamic evaluation is out of scope until a dedicated isolation design is reviewed. Any future execution must use disposable isolation, no network by default, strict CPU/memory/time limits, no host credentials, read-only input mounts where possible, and explicit user consent. A container alone should not be treated as a complete security boundary.

## Reporting

For a suspected vulnerability in SkillForge itself, follow [SECURITY.md](../SECURITY.md). Avoid publishing exploit details before a fix is available.
