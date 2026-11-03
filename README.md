# SkillForge — Evidence-based trust for AI agent skills

SkillForge is an open-source toolkit for inspecting AI agent skills and producing transparent, reproducible evidence about their structure, declared capabilities, and potential risks.

> **Status: early prototype (v0.1.1).** The current release performs static inspection only. It does not execute skill code and cannot prove that a skill is safe.

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
python -m pip install -e ".[dev]"
skillforge scan examples/demo-skill
```

Without installing the package:

```bash
python -m skillforge scan examples/demo-skill
```

JSON output:

```bash
skillforge scan examples/demo-skill --format json
```

Fail a CI job when a critical finding is present:

```bash
skillforge scan examples/demo-skill --fail-on critical
```

Available thresholds: `none`, `low`, `medium`, `high`, and `critical`. By default, findings do not fail the command; scan errors return exit code 2.

Run tests:

```bash
python -m pytest -q
```

## Current checks

| Rule | Severity | Meaning |
|---|---|---|
| SF001 | Critical | Shell download piped into an interpreter |
| SF002 | High | Recursive deletion targeting a broad path |
| SF003 | Medium | References to common credential locations |
| SF004 | Low | Common environment-variable access patterns |
| SF005 | Medium | Prompt or instruction override language |

See [the rule reference](docs/RULES.md) for limitations and contribution requirements. Findings are heuristic indicators for human review, not proof of maliciousness. False positives and false negatives are expected.

## Design principles

1. **Evidence over opaque scores.** Every finding should identify the rule, severity, location, and explanation.
2. **Reproducibility.** Traversal and findings are sorted; report paths are relative.
3. **Safe by default.** Static inspection must not execute untrusted skill code.
4. **Bounded input.** File reads, metadata size, and traversal entry count are limited.
5. **Honest limitations.** A clean report is not a safety guarantee.
6. **Small, reviewable steps.** Rules should be documented and tested.

The scanner skips common generated directories such as `.git`, `.venv`, `venv`, and `node_modules`, as well as symlinks. It scans supported text extensions only.

## Roadmap

- [x] Initial parser, static rules, CLI, tests, and CI workflow
- [x] Bounded file reads, traversal limits, symlink skipping, and deterministic findings
- [x] Basic multiline descriptions and duplicate metadata validation
- [x] CI matrix for Python 3.10–3.13
- [ ] Add rule confidence and matched evidence snippets
- [ ] Expand fixture corpus and false-positive regression tests
- [ ] Add baseline comparison between skill versions
- [ ] Design isolated dynamic evaluation (separate milestone; never run on the host)
- [ ] Publish reproducible benchmark protocol

## Security

Please read [the threat model](docs/THREAT_MODEL.md) and [security policy](SECURITY.md) before using SkillForge in a security-sensitive workflow. A clean scan is not certification.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions that improve test coverage, rule explanations, reproducibility, and safe handling of untrusted inputs are especially welcome.

## License

MIT. See [LICENSE](LICENSE).
