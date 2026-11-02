# Contributing to SkillForge

Thanks for helping make skill evaluation more transparent and reproducible.

## Development setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
python -m pip install pytest
python -m pytest -q
```

## Adding a scanner rule

1. Give the rule a stable ID (SF006, SF007, ...).
2. Document what evidence it detects and why it matters.
3. Add at least one positive test and one negative test.
4. Avoid claiming that a pattern proves malicious intent.
5. Keep scanning static; do not execute the input.

## Pull requests

Please keep changes focused, explain the security or usability impact, and include tests. For significant changes, open an issue first to discuss the approach.

## Code of conduct

Be respectful, constructive, and welcoming. Critique ideas and code, not people.
