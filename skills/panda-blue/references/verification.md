# Remediation verification

A fix claim is checked against the invariant, not a green suite. panda-red
`simulate` usually supplies the original negative/control pair; this skill reruns
it without contacting targets beyond what supplied evidence or an authorized lab
already covers.

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
