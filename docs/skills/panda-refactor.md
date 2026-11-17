# Panda Refactor

Panda Refactor carries a bounded structural improvement from evidence to
verification while preserving observable behavior and supported contracts. It
combines complexity assessment, planning, incremental edits, and testing around
the behavior that must stay stable. It is complete on its own.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Splitting responsibilities, removing duplication, untangling dependencies, moving module boundaries |
| **Not for** | Diagnosing a defect ([Debugger](panda-debugger.md)) or measured speedups ([Perf](panda-perf.md)) |
| **Edits by default** | Depends on the request: analysis and planning are read-only; "refactor X" authorizes scoped edits |
| **Check results** | PASS, FAIL, NOT RUN, BLOCKED, with reasons |
| **Valid result** | "No change needed", with justification |

## Request types

Mode names are optional; Refactor infers them from your wording.

| Request | Deliverable and editing boundary |
| --- | --- |
| ANALYZE | Evidence-backed findings and priorities; source and tests unchanged |
| DESIGN | Current and proposed responsibilities, alternatives, trade-offs; only a requested artifact is written |
| PLAN | Incremental plan with files, prerequisites, invariants, checks; no source or test edits |
| EXECUTE | Scoped code and test changes with baseline and incremental verification |
| REVIEW | Compatibility and correctness findings on a refactor diff; read-only unless repairs are requested |
| QUICK | A depth modifier; it keeps the requested outcome's permissions and necessary checks |

## The preservation loop

1. **Discover the problem and contract.** Responsibilities, public entry points,
   consumers, inputs/outputs, errors, permissions, state, side effects.
   Complexity costs are concrete, not stylistic.
2. **Define invariants and resolve contradictions.** Each material behavior maps
   to evidence and a check. If current behavior violates requirements, that
   pre-existing defect is disclosed: preserving it and fixing it are different
   outcomes, and a characterization test must not quietly make it a contract.
3. **Choose the smallest useful structure.** No change, a minimal improvement,
   and a larger alternative are compared only when the decision warrants it.
   Abstractions need real coupling or variation to justify them.
4. **Establish a baseline.** Relevant checks run before any edit; pre-existing
   failures are recorded. Discriminating tests are added for meaningful gaps
   when authorized.
5. **Implement and verify in increments.** One coherent change, inspect the
   diff, run checks, reconcile invariants, then the next change. Tests are never
   weakened to reach green.
6. **Check completion and stop.** Final diff, affected consumers, and the
   invariant-to-check map. Differential equality can preserve an existing bug;
   passing tests bound confidence to exercised behavior.

For public API moves, state or transaction changes, concurrency, or conflicting
sources, Refactor reads its
[compatibility guidance](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-refactor/references/compatibility.md).

## Examples

### Refactor with full verification

```text
$panda-refactor Refactor src/messages to remove forwarding layers. Preserve the
public imports, permission checks, error behavior and exact output. Run baseline
checks, make small changes, and report actual verification and remaining gaps.
```

### Analysis only

```text
$panda-refactor Analyze src/messages; do not edit.
```

### Plan only

```text
$panda-refactor Plan the extraction of tax rules from src/checkout into their own
module; do not implement.
```

A persisted plan defaults to `.panda-suite/plans/YYYY-MM-DD-<topic>.md`.

### Compare designs

```text
$panda-refactor Compare two ways to split the 1,200-line OrderService: by use case
or by aggregate. Show current and proposed responsibilities and trade-offs.
Write the comparison to docs/order-service-design.md only.
```

### Move a public module safely

```text
$panda-refactor Move utils/dates.py to core/time/dates.py. External packages import
the old path, so keep a compatible re-export. Run the tests and a check that the
old import still works.
```

### Review a refactor diff

```text
$panda-refactor Review this branch, which claims to be a pure refactor of the
billing module. Flag any observable behavior change. Read-only.
```

### Quick bounded edit

```text
$panda-refactor Quick: extract the duplicated retry loop in src/clients/a.py and
src/clients/b.py into one helper. Run the client tests.
```

"Quick" reduces depth, not contract checks.

### When existing behavior is wrong

```text
$panda-refactor Restructure src/discounts. Note: I think stacking two coupons is
currently allowed even though the policy forbids it.
```

Expect the pre-existing defect to be disclosed and a decision requested before
any behavior change; the structural work continues independently.

## Optional peer guidance

Refactor may load [Simplify](panda-simplify.md), [Plan](panda-plan.md),
[Execute](panda-execute.md), [Test](panda-test.md), [Impact](panda-impact.md),
or [Review](panda-review.md) guidance when deeper help is useful. None is
required, and missing peers never block the workflow. At commit time it uses
[Git](panda-git.md) guidance; implementation never authorizes commits or pushes.

## Related

- [Refactor design and evaluation](../panda-refactor.md)
