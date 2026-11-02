# Product specification — SkillForge

## Mission

Make the trust characteristics of AI agent skills easier to inspect, compare, and reproduce.

## Initial user

A developer evaluating a third-party or internally maintained agent skill before allowing it into a workflow.

## MVP

- Accept a local directory containing SKILL.md.
- Parse required name and description metadata.
- Inspect supported text files without executing them.
- Emit findings with stable rule IDs, severity, path, line, and rationale.
- Produce human-readable and JSON output.
- Run deterministic unit tests in CI.

## Non-goals for v0.1

- Proving a skill is safe.
- Running scripts embedded in a skill.
- Uploading skill contents to a hosted service.
- Assigning a universal trust score.
- Automatically blocking or approving skills.

## Later research questions

1. How should task utility be measured against a no-skill baseline?
2. Which runtime differences materially affect a skill's behaviour?
3. How should version-to-version regressions be represented?
4. What evidence is required for another team to reproduce an evaluation?

## Success measures

- Reproducible scanner output across repeated runs.
- High-quality, documented rules with a regression fixture for each rule.
- Clear distinction between observed evidence and inferred risk.
- External contributors can add a rule without changing core architecture.
