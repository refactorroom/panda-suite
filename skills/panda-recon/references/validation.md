# Simulation, bounty and remediation verification

## Simulate

Define invariant → hypothesis → synthetic environment/accounts → expected behavior
→ baseline → minimal negative/control pair → observations → evidence → conclusion.
Useful invariants include owner/tenant access, token expiry/revocation, safe path
handling, webhook signature/freshness and bounded request rates. Respect the
[engagement](engagement.md); localhost or a disposable workspace alone does not
authorize requests or isolate external dependencies.

Use synthetic account/object data. Avoid third-party records, real secrets and
destructive payloads. Record exact safe parameters and tool version; capture
baseline and challenge outcomes, failures and missing observations. A successful
simulation establishes only the tested invariant in that environment, not a real
incident or generalized exploitability. No P0 helper executes these scenarios.

Detection coverage requires evidence for both the simulated action and the
expected telemetry/alert path. Separate observed alert, missing expected alert,
missing telemetry and untested detection. Absence of an exported alert may reflect
collection gaps, sampling or latency; do not count it as a confirmed detection miss.

## Bounty

Inspect the applicable program policy/version for explicit assets, exclusions,
accounts, techniques, budgets and disclosure constraints. If unavailable or
contradictory, stay offline. Discovery does not authorize testing related assets.
Prepare a sanitized report with target/policy, prerequisite, invariant, safe
reproduction, expected/observed behavior, evidence, impact/severity, fix and limits.
Never claim novelty, eligibility, acceptance or payment from a technical finding.
Do not submit, contact the target or disclose externally without that authorization.

## Verify

Preserve the finding ID and original evidence. Recheck the same invariant against
the identified revised environment with the approved negative and safe control.
Record subject/configuration/version changes, actual results and regression/detection
evidence. Outcomes: Fixed, Still vulnerable, Partially remediated, Not reproducible,
Not tested or Inconclusive. A failed tool or changed/unavailable environment is not
Fixed. Static source evidence and executed validation are different claim strengths.

[OWASP WSTG](https://owasp.org/www-project-web-security-testing-guide/) and
[OWASP ASVS](https://asvs.owasp.org/) offer applicable methodology. Verify edition
and exact requirement before mapping; neither proves exploitability or compliance.
