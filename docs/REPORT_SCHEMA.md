# Scan report schema (version 1.0)

`skillforge scan <path> --format json` prints one JSON object. Keys are sorted, so output is stable and can be diffed.

## Top-level fields

- `schema_version`: version of this report format (`"1.0"`). Check it before parsing.
- `scanner_version`: SkillForge version that produced the report.
- `skill`: `name`, `description`, and `path` (always `"."`, so reports do not contain local paths).
- `summary`: `finding_count` and `error_count`.
- `findings`: ordered list of findings (below).
- `errors`: non-fatal inspection errors, such as a skipped file. Messages never contain absolute local paths.

## Finding fields

- `rule_id`: stable rule identifier, such as `SF001`. Identifiers are never reused.
- `title`: short rule name.
- `severity`: `low`, `medium`, `high` or `critical`.
- `confidence`: `low`, `medium` or `high`. How sure the rule is that its pattern matched as intended. It is not a probability that the skill is malicious.
- `message`: plain-language reason the text was flagged.
- `evidence`: the matched text only (not the whole line), at most 240 characters. It is untrusted skill content: escape it before showing it in a terminal or web page.
- `rule_reference`: path and anchor of the rule's documentation, such as `docs/RULES.md#rule-sf001`.
- `file_path`: path relative to the skill directory, with `/` separators.
- `line`: 1-based line number.

Findings are sorted by `file_path`, then `line`, then `rule_id`.

## Example

```json
{
  "errors": [],
  "findings": [
    {
      "confidence": "medium",
      "evidence": ".ssh/",
      "file_path": "SKILL.md",
      "line": 8,
      "message": "References a common credential or private-key location.",
      "rule_id": "SF003",
      "rule_reference": "docs/RULES.md#rule-sf003",
      "severity": "medium",
      "title": "Credential path reference"
    }
  ],
  "scanner_version": "0.2.0",
  "schema_version": "1.0",
  "skill": {
    "description": "Helps with remote access.",
    "name": "m07-ssh-key-read",
    "path": "."
  },
  "summary": {
    "error_count": 0,
    "finding_count": 1
  }
}
```

## Compatibility

- Adding fields is not a breaking change. Consumers must ignore fields they do not know.
- Removing or renaming a field, or changing its meaning, increases `schema_version`.
- The absence of findings is not proof of safety.

## Exit codes

See the README. In short: 0 means no finding met `--fail-on`, 1 means one did, and 2 means the skill could not be parsed or the scan had errors and no finding met the threshold.
