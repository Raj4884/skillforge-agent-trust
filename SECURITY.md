# Security policy

## Supported scope

The current supported release is the latest code on the repository's default branch. SkillForge is an early static-analysis prototype, not a security certification product.

## Reporting a vulnerability

Please do not publish exploit details in a public issue. Contact the repository maintainer through the GitHub profile and include:
- A concise description of the issue.
- Affected version or commit.
- Reproduction steps that do not expose real credentials or private data.
- Potential impact.

Please allow reasonable time for investigation and a fix before public disclosure.

## Safe use

- Treat scan targets as untrusted input.
- Run SkillForge with the least privileges needed.
- Do not interpret a clean scan as proof of safety.
- The current scanner does not execute skill scripts. Do not add dynamic execution without a separately reviewed isolation design.
