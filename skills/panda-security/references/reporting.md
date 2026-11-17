# Security reporting contract

For a normal audit, answer in Markdown. When saved reports are requested, honor
the destination and avoid overwriting existing evidence. If none is specified,
use `security-reports/SECURITY_AUDIT.md`, `THREAT_MODEL.md`,
`REMEDIATION_PLAN.md` and `findings.json`. Keep source files read-only. Review
reports for sensitive values before retention; no bundled tool guarantees redaction.

Markdown covers summary, scope/revision/context, threat model, prioritized findings,
confirmed versus unverified issues, scanner execution, remediation priorities,
regression checks and limitations. Avoid duplicating extensive prose across files.
Threat model: assets, attacker capabilities, entry points, privileges, boundaries
and plausible attack paths, with unavailable deployment/runtime evidence visible.

Use the [JSON schema](../assets/findings.schema.json) for machine-readable reports;
the [synthetic example](../assets/findings.example.json) illustrates its shape.
Schema validation checks structure, not the truth of evidence, secret removal,
path safety, deduplication or audit completeness. The schema is a report format,
not an Invaris, Evaris or Itervyn protocol.

Each finding records a stable ID, optional local rule ID, category/classification,
severity and rationale, confidence, locations/component, sanitized evidence,
attacker prerequisites, causal scenario, impact, controls considered, remediation,
regression and verification. Use `null` for unavailable line numbers, CWE or
revision/timestamp; do not invent values. Keep original IDs during rechecks.

For new IDs, prefer `SEC-` plus a short SHA-256 prefix of the normalized relative
path, symbol/component and root-cause category. Do not include secret bytes or
line numbers in ID input. Resolve collisions explicitly. Deduplicate one root
cause across scanners/locations while retaining materially different causes.

Classification is Confirmed vulnerability, Likely vulnerability, Hardening,
Informational or False positive. Unassessed coverage goes in `coverage`/limitations,
not an invented finding. Confirmed means a supported code/configuration path or
applicable advisory, not observed exploitation. Severity is Critical/High/Medium/
Low/Informational with practical rationale, independent of Confirmed/Likely/Unknown
confidence. Hardening or rejected candidates must not inflate vulnerability counts.

Verification status records source-traced, reproduced, advisory-matched, fixed,
still-present, not-reproducible or unverified plus the deciding evidence/gap.
Do not mark fixed from a commit message or green tests alone. A useful regression
fails on the vulnerable behavior and passes on the repaired/control behavior in
a safe environment. Proposed tests stay unrun until actually executed.

Scanner rows preserve command/version, Completed/Failed/Not Run, exit code or null,
sanitized evidence and limits. Completed describes tool completion, not a clean
audit. Preserve nonzero finding exits separately from errors and report offline,
unavailable, denied, truncated and malformed results honestly. Do not copy raw
secret-bearing scanner logs into reports.
