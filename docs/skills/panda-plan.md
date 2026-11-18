# Panda Plan

Panda Plan converts agreed requirements into work an engineer can execute:
ordered tasks with dependencies, file locations, acceptance criteria, and
discriminating verification. It also reviews and archives completed or
explicitly superseded plans.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Ordered implementation tasks, release gates for a defined boundary, tidying saved plans |
| **Not for** | An unclear product need ([Brainstorm](panda-brainstorm.md)), a contract alone ([Spec](panda-spec.md)) |
| **Edits by default** | Only the plan file (and a `/.panda-suite/` ignore rule). Never source or tests |
| **Saved to** | `.panda-suite/plans/YYYY-MM-DD-<topic>.md`, unless you name another path or ask for chat only |
| **Readiness labels** | EXECUTION-READY, PARTIALLY READY, BLOCKED |

## How it works

1. **Understand requirements.** Intended behavior, non-goals, compatibility
   promises, mandatory acceptance. Supplied requirement IDs are kept; facts,
   proposals, assumptions, and open decisions are labeled.
2. **Inspect the system.** Source, callers, test assertions, configuration, and
   project instructions, with cited paths. Existing capabilities are reused.
3. **Define scope and contracts.** Interfaces, source of truth, data ownership,
   invariants, dependency direction, failure and recovery. Changed public
   boundaries state compatibility promises and their checks.
4. **Order coherent tasks.** Each task has an ID, title, outcome, requirement
   references, files, prerequisites, acceptance, and verification. Dependent tasks
   state what they consume and produce with exact names and signatures, so an
   implementer can act from that task alone.
5. **Plan discriminating verification.** For each critical behavior, a
   plausible wrong implementation and the check that rejects it. Commands come
   from repository tooling; unavailable environments are labeled.
6. **Check the plan.** Every requirement maps to a task, every acceptance
   condition to a check and expected evidence (a Requirement, Task, Check,
   Evidence table for complex work). Omitted, null, empty, and invalid inputs are
   distinguished where outcomes differ, and the language must actually be able to
   produce the promised error. A scope change is applied through the whole
   artifact and stale references are removed.

## Plan readiness

| Label | Meaning |
| --- | --- |
| **EXECUTION-READY** | No unresolved decision blocks authorized implementation |
| **PARTIALLY READY** | Named tasks can start; others are blocked by named decisions |
| **BLOCKED** | Critical scope or contract decisions prevent execution |

Plan always names the first unblocked task. These labels describe the plan, not
release readiness.

## Release gates

For a release, deployment, migration, or compatibility boundary, Plan adds
proportional gates (Gate, Required condition, Verification and expected
evidence, Blocking, Revision/environment), marked **defined; evidence pending**.
[Release](panda-release.md) later evaluates the actual revision.

## Execution handoff

A saved plan ends by asking you to review it and choose how
[Execute](panda-execute.md) should run it:

- **Subagent-driven:** a fresh implementer and a fresh reviewer per task, then
  one whole-change review. Most thorough; offered only when the host can delegate.
- **Native:** this session implements every task, then one review. Cheapest
  and fastest.

Plan recommends one and gives a ready request. Saving a plan does not authorize
implementation by itself.

## Examples

### Plan from requirements

```text
$panda-plan Plan docs/approval-requirements.md against src/approvals and its tests.
Include ordered tasks, dependencies, file locations, acceptance criteria and
verification per task. Preserve existing callers. Save docs/approval-plan.md;
do not implement the feature.
```

### Small change, one task

```text
$panda-plan Plan adding a --dry-run flag to the import CLI. Keep it to one task
with inline checks.
```

Expect a single task with source, contract, acceptance, and checks inline, with
no ceremonial sections.

### Plan with release gates

```text
$panda-plan Plan the migration from integer order IDs to UUIDs, including
release gates for the database migration and mixed application versions.
```

### Error contract precision

```text
$panda-plan Plan a validate_discount(code) function. Missing, empty, unknown and
expired codes must each produce a distinct, documented error.
```

Expect separate handling for each case and a check that the proposed signature
can actually produce each promised error.

### Choose the execution mode up front

```text
$panda-plan Plan the bulk CSV import from docs/import-requirements.md. I want
subagent-driven execution afterwards.
```

Plan keeps your mode and asks only for review.

### Chat-only plan

```text
$panda-plan Give me a plan in chat only for adding rate limiting to the login
endpoint. Do not save a file.
```

### Apply a scope decision

```text
$panda-plan Remove CSV export from .panda-suite/plans/2026-11-12-reports.md;
only PDF is in scope now.
```

Expect the change applied to goals, tasks, dependencies, checks, and gates, with
no stale CSV references left.

### Review and archive finished plans

```text
$panda-plan Process the plans in .panda-suite/plans. Archive the ones that are
complete and verified against current source; leave the rest active and tell me
what remains in each.
```

Checked boxes alone do not prove completion. Verified plans move to
`.panda-suite/plans/archive/`; unfinished plans stay active.

### Archive a superseded plan

```text
$panda-plan The 2026-10-02 search plan is superseded by the 2026-11-10 plan.
Archive the old one.
```

An explicit supersession decision permits archiving with unchecked tasks; the
report distinguishes supersession from completion.

## Boundaries

Planning authorizes the plan artifact, not implementation. Plan does not edit
source or tests, does not estimate duration without evidence, and requires no
commit. When it saves under `.panda-suite`, it ensures the root `.gitignore`
contains `/.panda-suite/` and verifies it with `git check-ignore`.

## Related

- [Planning refinement and trial limits](../panda-plan-refinement.md)
- [Plan archive design](../panda-plan-archive.md)
- [Execute](panda-execute.md), [Release](panda-release.md)
