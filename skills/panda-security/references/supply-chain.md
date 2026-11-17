# Dependencies, CI/CD and infrastructure

Establish who controls each input and which identity, secret, artifact or deployment
it can affect. Review applicable surfaces; do not assume every project deploys a web app.

| Surface | Trace and verify |
| --- | --- |
| Dependencies | Resolved version/source, lockfile, transitive path, install/build hooks, integrity/provenance and authoritative advisory applicability. Dev tools may execute in privileged CI. |
| CI events | PR/fork/branch trust, privileged trigger semantics, checkout/ref, attacker-controlled arguments, cache poisoning and execution before secret access. Event names alone are insufficient. |
| Workflow authority | Effective token/cloud/OIDC privileges, claim restrictions, environment approval and reusable workflow/action sources. Assess mutable refs against the actual threat model. |
| Build/release | Untrusted artifacts promoted to signing/deployment, provenance checks, protected inputs, credential exposure and destination access. |
| Containers | Build context/secrets, image origin, sockets/volumes, privileged mode, runtime user/capabilities and exposed services. Root alone is not a demonstrated exploit. |
| Infrastructure | Effective IAM/resource policy, public ingress, secret/state files, dangerous defaults, environment separation and privileged provisioning. |

Separate vulnerabilities from hardening such as pinning and least privilege.
Static audit authority does not authorize pipelines, image builds, provisioning,
artifact downloads or cloud API access. A clean scanner proves no absence of risk.

[OpenSSF Scorecard](https://github.com/ossf/scorecard) supplies optional repository
practice evidence, not vulnerability verdicts or permission to query private repos.
