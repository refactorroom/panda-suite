# Optional handoffs

Companions improve a relevant activity without becoming dependencies. Load their
actual instructions using the host; do not invent an invocation API or start a
mandatory multi-agent pipeline.

| Peer | Handoff |
| --- | --- |
| panda-security | Source/configuration audit with exact scope; import IDs, evidence and unverified status without upgrading confidence. panda-blue owns hunting, incident reconstruction, fix verification and dated intelligence; Security may use `intelligence.json` for dependency triage inside its audit. |
| panda-red | Surface mapping, lab validation and bounty preparation under an engagement. Hand over case records, finding IDs and hypotheses that need active checks; case/evidence/finding records validate in both skills. |
| panda-debugger | A specific application execution/root-cause question and its safe evidence; incident suspicion alone does not authorize code execution or repairs. |
| panda-write | Sanitized structured findings and explicit report paths; writing must not discover or invent vulnerability facts. For intel reports pass `intelligence.json` and `source-status.json` and keep every source URL, date and freshness status. |
| panda-plan | Prioritized supported issues and acceptance invariants for a requested detailed remediation plan. |
| panda-refactor / panda-execute | Explicitly approved scoped code changes and regression criteria; structural refactoring is not automatically a vulnerability fix. |
| Invaris | Candidate deterministic invariants and benign challenges; inspect the actual CLI/schema and trusted commands before running. |
| Evaris | Labeled fixtures, independent keys, actual imported agent results and comparable conditions. Prepare/import alone does not run an agent. Compute recall/false-positive rates only with relevant ground truth and denominators. |
| Itervyn | Optional supported verification providers and evidence. Check actual version compatibility; do not translate advisory next actions into unbounded attack/repair loops. |

P0 creates no adapters. Future integrations must preserve tool exits, failure and
inconclusive states, evidence subject identity, permissions and privacy. A scratch
workspace is not a sandbox. Never infer that latest tool versions work together.
