# Scanner rules

Rules are heuristic signals for manual review, not a malware verdict. Confidence
describes confidence that the pattern matched as intended; it is not a probability
that a skill is malicious.

## Rule reference

<a id="rule-sf001"></a>

### SF001 — Download piped to shell
- Severity: Critical; confidence: High.
- Signal: curl or wget piped into a shell interpreter, including common sudo,
  /bin/sh, and process-substitution forms.
- Limitation: Does not detect every download-and-execute technique.

<a id="rule-sf002"></a>

### SF002 — Recursive deletion of broad target
- Severity: High; confidence: High.
- Signal: rm with a recursive option targeting /, a top-level system directory,
  or the home directory itself.
- Limitation: Detects recursion, not necessarily the -f flag. Specific project
  paths such as /tmp/build are not flagged. Complex shell expansion may evade it.

<a id="rule-sf003"></a>

### SF003 — Credential path reference
- Severity: Medium; confidence: Medium.
- Signal: References to common SSH, AWS, Google Cloud, or npm credential paths.
- Limitation: A path reference may be documentation or a legitimate operation.

<a id="rule-sf004"></a>

### SF004 — Environment access
- Severity: Low; confidence: Low.
- Signal: Common access patterns such as os.environ, os.getenv, process.env,
  ENV[], printenv, or env as a command.
- Limitation: Environment access is often legitimate; this does not prove a
  secret was read or transmitted.

<a id="rule-sf005"></a>

### SF005 — Instruction override language
- Severity: Medium; confidence: Medium.
- Signal: Phrases resembling attempts to override prior or system instructions.
- Limitation: Legitimate defensive documentation may match.

## Finding fields

Each finding includes stable rule ID, severity, qualitative confidence, bounded
matched evidence, explanation, rule-reference URL, relative file path, and
1-based line number. Evidence is untrusted source text and must be escaped in
terminals and web pages. Confidence is not a calibrated statistical score.

Every new rule needs positive and benign negative fixtures, severity rationale,
known bypasses, false-positive notes, and linear-time matching. Rule IDs are
stable and must never be silently reused. Matching is line-based.
