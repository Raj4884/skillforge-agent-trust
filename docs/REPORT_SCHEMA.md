# Scan report schema (v0.1)

The JSON report contains:

- `scanner_version`: SkillForge version that produced the report.
- `skill`: `name`, `description`, and local `path`.
- `summary`: total finding and error counts.
- `findings`: ordered observations with rule ID, title, severity, message, file path, and 1-based line.
- `errors`: non-fatal inspection errors.

The schema is an early prototype and may change before a stable 1.0 release. Consumers should preserve unknown fields and should not treat the absence of findings as proof of safety.
