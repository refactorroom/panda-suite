# Security scan

## Executive summary

Assessment: Partial. 3 canonical findings; 2 displayed.
Zero findings is not proof of security.

## Scope and environment

Bounded local target; 5 files inventoried. No target or advisory service contacted.

## Scan methodology

Depth: quick. Supplied findings normalized; manual causal review remains necessary.

## Tools executed

None by this helper. Imported producer claims are not helper-executed scans.

## Findings by severity

- Critical: 0 canonical.
- High: 2 canonical.
- Medium: 0 canonical.
- Low: 0 canonical.
- Informational: 1 canonical.

## Detailed findings

### F-306a67c7414ebb78 — Static scanner concern requiring review

High; Unknown; Potential concern; category: source-security.
- Location: app.py; lines 4–4 (null means unavailable).
- Evidence IDs: E-ebbb069a5e600757
- Impact: Not established from a scanner match alone.
- Recommendation: Confirm the causal path and controls before selecting remediation.
- Controls considered: Not yet assessed; trace relevant guards and caller controls before confirmation.
- Verification: Not tested

### F-7f9660a2da53d6d5 — Potential credential exposure

High; Unknown; Potential concern; category: secrets.
- Location: config.env; lines 1–1 (null means unavailable).
- Evidence IDs: E-96a80bc0093c14a7
- Impact: Not established from a scanner match alone.
- Recommendation: Confirm the causal path and controls before selecting remediation.
- Controls considered: Not yet assessed; trace relevant guards and caller controls before confirmation.
- Verification: Not tested

## Evidence and reproduction status

Locations and ranges were checked against current source. Imported report execution and claims remain unverified.

## Recommended remediation

Prioritize supported practical impact; manually reject false positives before changing source.

## Suggested regression tests

- F-306a67c7414ebb78: Use a safe negative/control pair against the verified invariant; not run.
- F-7f9660a2da53d6d5: Use a safe negative/control pair against the verified invariant; not run.

## Assessment limitations

- Local inventory and supplied-result normalization only; manual analysis/coverage remains unverified.
- No current dependency advisory lookup or runtime validation was performed.
- Trusted-root, non-concurrent filesystem assumptions apply; this helper is not a sandbox.
- Severity filtering affects this view only; findings.json retains every normalized finding.
- Automatic masking is conservative; review narrative/paths for unrecognized sensitive data before sharing.
