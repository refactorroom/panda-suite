# Panda Execute

Panda Execute delivers authorized changes and evidence of their behavior. It
implements an approved plan or a clearly scoped request, preserving task
dependencies, existing conventions, acceptance criteria, and honest
verification status.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Implementing a saved plan, or a clear implementation request |
| **Not for** | Planning-only, investigation-only, or review requests (they do not authorize edits) |
| **Edits by default** | Relevant reversible workspace changes once you ask for implementation |
| **Modes for a saved plan** | Native (default) or subagent-driven |
| **Status labels** | implemented, verified, partially verified, blocked, not started |

## Before changing files

Execute reads the plan, acceptance criteria, project instructions, current
source, tests, and working-tree state. It preserves your existing edits. A clear
request to implement counts as authorization; it does not ask again. For a small
change without a plan it states a compact task sequence and proceeds.

## Running a saved plan

The plan is the contract. Execute implements every task in order with the
files, names, signatures, tests, and values it states, and does not rename,
merge, or redesign silently.

- Task checkboxes are ticked only after that task's checks pass.
- On resume, it re-runs checks for tasks already marked done, then continues from
  the first unchecked task.
- Necessary deviations are recorded under a "Deviations" heading in the plan.
- It continues to the last task without pausing to ask whether to go on.

| Mode | How it runs |
| --- | --- |
| **Native** (default) | This session implements every task, then reviews the whole diff (with a fresh reviewer when the host can delegate) |
| **Subagent-driven** | A fresh implementer per task gets only that task, its interfaces, the constraints, and paths. Execute re-runs the checks itself, then a fresh reviewer checks the task before the next one. One whole-change review at the end. Falls back to native, and says so, if the host cannot delegate |

## Execution loop

1. Select the next unblocked task; name its objective and acceptance.
2. Make the smallest coherent change that follows existing conventions. Add or
   update tests that meaningfully detect the behavior.
3. Run the actual repository checks. Expected outcomes come from the contract,
   not from the implementation. If the suite misses a required behavior, Execute
   runs a focused discriminating check, keeping supplied tests intact.
4. Record the status and continue with work whose dependencies are met.
5. Review the finished diff for omissions and unwanted changes.

If evidence contradicts the plan, affected work stops and you get the
contradiction and a revised approach. A material change of scope needs your
decision; once you decide, the plan is updated throughout before work continues.

## Examples

### Implement a saved plan (native)

```text
$panda-execute Implement docs/approval-plan.md. Preserve existing API callers,
update relevant tests, and run the repository checks. Report actual commands,
acceptance status and unrun checks. Do not deploy or publish.
```

### Subagent-driven run

```text
$panda-execute (subagent-driven) Implement .panda-suite/plans/2026-11-12-bulk-csv-import.md.
```

### Resume an interrupted plan

```text
$panda-execute Continue .panda-suite/plans/2026-11-12-bulk-csv-import.md from
where the last session stopped.
```

Expect the completed tasks' checks to be re-run before work resumes at the
first unchecked task.

### A small change without a plan

```text
$panda-execute Add a --limit option to scripts/export.py that caps rows written.
Default stays unlimited. Add a test and run the suite.
```

### Change scope mid-plan

```text
$panda-execute Drop task T4 (email notifications) from the current plan; we will
do it next quarter. Continue with the rest.
```

Your decision is applied to the plan (tasks, checks, handoff) and recorded
briefly before execution continues.

### Fix with diagnosis

```text
$panda-execute Fix the failing test in tests/test_invoices.py. Find the cause
before changing code; do not edit the test.
```

Execute establishes what failed and why before changing code, and may use
[Debugger](panda-debugger.md) guidance if installed.

### Implement and prepare a commit message

```text
$panda-execute Implement the plan, then propose a commit message. Do not commit.
```

[Git](panda-git.md) guidance is loaded for the message; implementation never
authorizes commits or pushes by itself.

## Delivery report

What changed and why, acceptance status, commands with actual results, unrun
checks with reasons, incomplete tasks, and material risks. A test is never
called passed before it finishes successfully, and a green suite is reported
separately from acceptance completeness.

## Boundaries

Destructive actions, production changes, deployment, publishing, and external
side effects need authorization covering them. Local implementation does not.

## Related

- [Plan](panda-plan.md) to create the contract Execute follows
- [Test](panda-test.md), [Review](panda-review.md) for focused follow-up
