# Panda Review

Panda Review finds actionable defects introduced or exposed by a change: a pull
request, a diff, or another bounded comparison. It checks correctness, security,
reliability, data integrity, compatibility, and regression risk, each with
precise evidence.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | PR review, reviewing your own branch before merge, checking a diff against a requirement |
| **Not for** | Complexity advice without a defect ([Simplify](panda-simplify.md)), a dedicated vulnerability or dependency audit ([Security](panda-security.md)) |
| **Edits by default** | None. Review does not authorize fixes |
| **Main output** | Prioritized findings, or a short "no significant findings" result with review limits |
| **Never does** | Invent findings to fill a report, or present speculation as a confirmed vulnerability |

## How it works

1. **Understand intent.** Requirements and repository guidance, the diff, and
   the affected callers, contracts, state transitions, and tests.
2. **Trace behavior.** Validation, authentication and authorization, errors,
   transactions, concurrency, data integrity, API compatibility, and operations
   where relevant. Expected behavior comes from the contract before existing
   tests are trusted: passing tests alone do not prove correctness.
3. **Validate candidates.** The triggering input or condition is traced through
   real code and existing guards, with a focused safe reproduction when useful.
   Findings already prevented by the code, or based only on preference, are dropped.
4. **Report by impact.** Material defects before style, with precise file and
   line locations.

## Finding format

| Field | Content |
| --- | --- |
| **Severity** | critical (immediate severe compromise or data loss), high (core correctness or security), medium (a bounded path), low (limited impact) |
| **Location and issue** | File/line and the faulty behavior |
| **Trigger and evidence** | The input or state that triggers it and the causal path, including mitigations considered |
| **Impact and correction** | The consequence and the smallest appropriate repair |

For example: removing an owner check lets a non-owner cancel an unshipped order
when no caller guard exists. The finding cites the changed function and the
caller contract, not just "missing security".

## Examples

### Branch against a requirement

```text
$panda-review Review the current branch against origin/main for the owner-only
cancellation requirement. Trace changed behavior and callers. Report material
defects with severity, precise location, trigger, evidence, impact and correction.
Do not fix code.
```

### Current uncommitted diff

```text
$panda-review Review the current diff for material defects.
Explain the trigger, impact, and location of each finding. Do not fix code.
```

### A pull request

```text
$panda-review Review PR 128 (branch feature/bulk-import against main). Focus on
data integrity during partial failures.
```

### A specific commit range

```text
$panda-review Review commits a1b2c3d..HEAD. These should be a pure refactor;
flag any observable behavior change.
```

### Compatibility focus

```text
$panda-review Review the API changes in this branch for backward compatibility
with existing mobile clients. Use docs/api.md as the contract.
```

### Concurrency and transactions

```text
$panda-review Review the new payment retry logic for double-charge risks under
concurrent requests and process restarts.
```

### Review, then fix

```text
$panda-review Review the diff, then fix the high and critical findings only and
re-run the tests.
```

Fixes need explicit authorization like this; review alone never edits code.

### Under pressure to approve

```text
$panda-review We need to merge this in ten minutes. Is it safe?
```

Time pressure does not change the evidence. Expect the relevant guards inspected
and supported findings reported, or a clear "no significant findings" with limits.

## Boundaries

Application files stay unchanged unless fixes are requested. External or
destructive verification needs authorization. A small diff review never implies
a whole-system audit; the reviewed range is always stated.

## Related

- [Security](panda-security.md) for a dedicated audit
- [Test](panda-test.md) to add the tests a finding shows are missing
