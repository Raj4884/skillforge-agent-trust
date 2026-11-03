# Threat model

## Scope
SkillForge v0.2 statically inspects local skill files. It never executes skill code.

## Assets
- Developer workstation and local files.
- Credentials available to the environment.
- Integrity of scan reports and confidentiality of skill source.

## Trust boundaries
All skill content, filenames, metadata, and embedded snippets are untrusted data.

## Safeguards
- No skill code is imported or executed.
- SKILL.md reads are bounded to 256 KB; scanner files to 1 MB; traversal to
  10,000 entries.
- Supported text extensions only; symlinks and common generated directories skipped.
- Deterministic findings, relative paths, bounded evidence snippets.
- Terminal output escapes control and invisible-format characters.
- Error messages avoid exposing absolute local paths.

## Limitations
- Parser is a limited dependency-free YAML-frontmatter parser, not full YAML.
- Static patterns cannot understand all program semantics; obfuscated, indirect,
  encoded, or multi-line behaviour may evade detection.
- False positives are expected. Confidence is qualitative, not calibrated risk.
- Filesystem protections are best-effort across operating systems.
- A clean report is not certification or a safety guarantee.

## Future dynamic evaluation
Out of scope until a dedicated isolation design is reviewed. Any future execution
must use disposable isolation, no network by default, strict resource limits,
no host credentials, read-only input mounts where possible, and explicit consent.
A container alone is not a complete security boundary.
