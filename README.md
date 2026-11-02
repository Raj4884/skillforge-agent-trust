# SkillForge — Evidence-based trust for AI agent skills

SkillForge is an open-source toolkit for inspecting AI agent skills and producing transparent, reproducible evidence about their structure, declared capabilities, and potential risks.

> **Status: early prototype.** The current release performs static inspection only. It does not execute skill code and cannot prove that a skill is safe.

## Why SkillForge?

Agent skills can influence what an AI system reads, writes, executes, and sends. A single opaque “trust score” is not enough. SkillForge aims to make review evidence inspectable and repeatable.

The long-term project investigates four questions:

- **Safety:** What risky commands, credential references, or instruction patterns are present?
- **Utility:** Does a skill measurably improve completion of a defined task?
- **Compatibility:** Does it behave consistently across supported agent runtimes?
- **Regression:** Did a skill update change its risk or task performance?

The first milestone focuses on a safe, local static scanner for skills containing a `SKILL.md` file.

## Quick start

Requires Python 3.10 or newer.

```bash
git clone https://github.com/Raj4884/skillforge-agent-trust.git
cd skillforge-agent-trust
python -m pip install -e .
skillforge scan examples/demo-skill
```

Without installing the package:

```bash
python -m skillforge scan examples/demo-skill
```

JSON output:

```bash
python -m skillforge scan examples/demo-skill --format json
```

Run tests:

```bash
python -m pytest
```

## Current checks

| Rule | Meaning |
|---|---|
| SF001 | Shell download piped into a shell interpreter |
| SF002 | Recursive force deletion pattern |
| SF003 | References to common credential locations |
| SF004 | Broad environment-variable access |
| SF005 | Prompt or instruction override language |

Findings are heuristic indicators for human review, not proof of maliciousness. False positives and false negatives are expected in this early version.

## Design principles

1. **Evidence over opaque scores.** Every finding should identify the rule, severity, location, and explanation.
2. **Reproducibility.** The same input and scanner version should produce the same report.
3. **Safe by default.** Static inspection must not execute untrusted skill code.
4. **Honest limitations.** A clean report is not a safety guarantee.
5. **Small, reviewable steps.** Rules should be documented and tested.

## Roadmap

- [x] Initial parser, static rules, CLI, tests, and CI workflow
- [ ] Harden path traversal, symlink handling, and file-size limits
- [ ] Add structured rule metadata and stable report schema
- [ ] Add fixture corpus and false-positive regression tests
- [ ] Add baseline comparison between skill versions
- [ ] Design isolated dynamic evaluation (separate milestone; never run on the host)
- [ ] Publish reproducible benchmark protocol

## Security

Please read [the threat model](docs/THREAT_MODEL.md) before using SkillForge in a security-sensitive workflow. Report suspected vulnerabilities privately to the repository maintainer rather than posting exploitable details in a public issue.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions that improve test coverage, rule explanations, reproducibility, and safe handling of untrusted inputs are especially welcome.

## License

MIT. See [LICENSE](LICENSE).
