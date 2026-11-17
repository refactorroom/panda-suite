# Verification harness security

Load for command runners, guards, graders, mutation/challenge campaigns and
evidence aggregation. A harness can be audited without executing it. Keep
security audit, deterministic guard verification and agent-quality evaluation
as separate claims. A scratch directory or policy name does not establish isolation.

## Execution and evidence contract

| Boundary | Evidence and negative check to seek |
| --- | --- |
| Configuration → execution | Who can edit harnesses, guards, oracles, executables or dependencies? Can a checkout supply a relative program or affect PATH? Inspect explicit shell use even with literal argv. |
| Process → environment | Effective variable allowlist, credential inheritance, cwd, executable identity, network/filesystem access and dependency links outside scratch. |
| Process lifecycle → verdict | Timeout, cancellation, stream bounds, signals, exit/report mismatch, missing output and detached descendants. PASS data cannot override execution failure. |
| Path → evidence | Traversal, symlinks/special files, trusted anchors, rooted access, exclusive writes, entry/size limits and concurrent replacement. Never open arbitrary provider finding paths automatically. |
| Evidence → subject | Config/executable identity, input/final-tree hashes, revision/dirty-state limits, schema/semantic validation and required criteria. Hashes identify bytes, not an honest author or tool. |
| Requirement → acceptance | Required/optional checks, empty scope, skipped work, weak markers and uncovered invariants. Passing baseline does not prove violation detection. |
| Evaluation → context | Frozen private oracles, reviewer controls, separate case/arm contexts, comparable tools/access and actual transcripts. Directory separation alone is not a same-user security sandbox. |
| Storage → publication | Private permissions, sensitive raw streams, complete/committed records, immutable history and sanitized sharing. Preserve original evidence/hash relationships privately. |

For contract failures, propose a benign negative control where the ordinary suite
passes despite a violated requirement, plus a correct control rejecting it. Do not
weaken requirements, repair evidence or replace an unfavorable trial.

## Panda ecosystem: inspect the version in use

These are audit prompts grounded in source projects, not required adapters. Locate
the selected checkout/configuration and matching source, schemas, CLI usage and
compatibility docs. Installed binaries may lag the checkout; unsupported flags and
mismatched schemas are limitations, never success.

- **Invaris:** inspect `docs/harness-spec.md`, `docs/threat-model.md`, schemas,
  `internal/runner/` and the selected action's engine. Commands run with user
  privileges. `networkPolicy` and `writablePaths` do not sandbox commands;
  replacement/copy restrictions have narrower meanings. Check input/evidence
  versions, structured policy/target counts, required gates, weak markers, cleanup,
  PROVEN/UNPROVEN/INCONCLUSIVE and mutation outcomes. Campaign scores cannot hide
  excluded or ineligible experiments.
- **Evaris:** inspect `docs/security.md`, `docs/invaris.md`, process/graders,
  filesystem import and comparison code. Prepare/import does not launch agents.
  Command grading/verification requires its opt-in and trusted programs; scratch
  copies, linked dependencies and snapshot exclusions are not containment. Audit
  frozen private oracles, allowed changes/protected paths where supported, imported
  metadata, comparable conditions and required criteria. Raw evidence may contain
  secrets. Invaris ACCEPT cannot replace failed/missing task criteria. Check the
  restricted verifier profile; standalone Invaris features are not automatically
  supported by Evaris.
- **Itervyn:** inspect `docs/security.md`, `docs/configuration.md`, provider
  contracts, process execution, aggregation and evidence publication. Verify exact
  supported provider versions/profiles, not just newest binaries. A live project
  and an imported Evaris run are different subjects. Required failures, inconclusive
  results and publication errors must survive aggregation. Check complete-record
  markers, evidence identity and `inspect` behavior. Advisory next actions do not
  authorize an autonomous repair loop.

Do not run harnesses to discover whether their commands are trusted. Prefer static
review and inert controls; execute reviewed local checks within existing permission.
Integrations remain optional until real compatible execution is observed; do not
invent APIs or automatic skill invocation.
