# Panda Craft

*Compose the expertise. Preserve the discipline. Verify the outcome.*

Panda Craft coordinates specialists that **you select explicitly**, Panda skills
or external ones, toward one shared outcome. Each specialist keeps its own
method, scope, and verification budget. Craft owns the outcome contract,
the handoffs between activities, and the final acceptance check.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Combining named skills (for example Execute + Test, or an external design skill) under one acceptance contract |
| **Not needed for** | A focused task with one specialist, or general workflow selection (use [Lead](panda-lead.md)) |
| **Edits by default** | Only what your request authorizes; naming an execution skill does not grant edit permission by itself |
| **Main output** | Delivered artifacts, skills actually loaded, observed checks, and a VERIFIED / PARTIALLY VERIFIED / BLOCKED / NOT VERIFIED status |
| **Requires** | The selected skills to be installed; missing ones are reported, never imitated |

## Craft or Lead?

| Situation | Choose |
| --- | --- |
| You do not know which skills you need | Lead |
| You know exactly which specialists to combine | Craft |
| You want to bring in a non-Panda skill (for example `$impeccable`) | Craft |
| One specialist covers the task | That specialist directly |

Neither is a prerequisite for the other.

## How it works

Craft follows the four Iddhipāda disciplines as working guidance, not as four
mandatory stages:

1. **Chanda (intent).** Establish the outcome, deliverables, constraints,
   non-goals, and observable acceptance criteria. For small tasks this is a
   short working note, not a plan document. Satisfactory earlier work is reused.
2. **Compose.** Read each selected skill's actual instructions through the host's
   discovery mechanism (including plugin namespaces). Order dependent
   activities, give each a deliverable and completion check. Host and user
   instructions come first; within them each specialist keeps its methods and
   limits. A specialist cannot enlarge authorization.
3. **Viriya + Citta (sustained execution).** Do the authorized work with each
   specialist's method. At each transition carry only the objective, verified
   facts, current artifacts, decisions, unknowns, the next action, and the exact
   authorization. Current source outranks a stale handoff.
4. **Vīmaṃsā (examine and adjust).** Compare the delivered work with every
   material acceptance criterion using real evidence. A green suite may omit a
   requirement, so Craft looks for a discriminating check where authorized. It
   respects each specialist's retry ceiling and reports unmet criteria instead
   of starting another polish cycle.

When the work reaches commits, Craft loads [Panda Git](panda-git.md) guidance if
available. Implementation alone never authorizes commits, pushes, or history
rewrites.

## What to provide

- The specialists to compose, using the selectors your host discovered.
- The shared outcome and acceptance criteria.
- Constraints (contracts to preserve, files not to touch).
- Allowed changes and checks to run.

## Examples

### Implement and verify a plan

```text
$panda-craft $panda-execute $panda-test
Implement docs/approved-plan.md and verify every material acceptance rule.
Local code, tests and documentation may change. Preserve API contracts.
Run local checks and the usage example; report unavailable integration checks.
```

Expect the implementation, tests derived from acceptance rules (not only from
the code), executed results, and a verification status for the whole outcome.

### Compose with an external design skill

```text
$panda-craft $impeccable
Refine this dashboard's hierarchy, responsiveness and keyboard navigation.
Local UI edits are allowed. Preserve business logic and API contracts.
Inspect the rendered result within Impeccable's verification budget.
```

Craft loads the external skill's own instructions and keeps its verification
budget. Expect rendered-result evidence for desktop, mobile, and keyboard use.

### Read-only investigation with two specialists

```text
$panda-craft $panda-debugger $panda-impact
Explain why nightly exports time out and what would break if we move them to a
queue. Do not change source or configuration.
```

Naming several skills does not grant edits. Expect a cause analysis plus a
dependency assessment, both read-only.

### Refactor, then document

```text
$panda-craft $panda-refactor $panda-write
Extract the pricing rules from src/checkout into one module without changing
behavior, then update docs/pricing.md to match. Code, tests and that doc may
change. Report PASS/FAIL/NOT RUN for each check.
```

Expect baseline checks before edits, incremental verification, and a document
that describes the new structure from current source.

### Logo plus UI implementation

```text
$panda-craft $panda-logo $impeccable
Create a mark for Tide Ledger, then apply it to the app header and favicon.
Local brand and UI files may change. Do not publish or deploy.
```

### Security fix with verification

```text
$panda-craft $panda-security $panda-execute $panda-test
Fix SEC-1a2b3c (missing tenant check in src/api/invoices.py) from
security-reports/findings.json. Add a regression test that fails without the
fix, then run "verify" on the original finding. Local code and tests may change.
```

Expect the fix, a discriminating regression test, and a Security `verify` result
that preserves the original finding ID.

### When a selected skill is missing

```text
$panda-craft $panda-perf $some-profiler-skill
Find why the report endpoint uses 2 GB of memory and propose a patch.
```

If `$some-profiler-skill` is not installed, Craft says it could not be loaded,
continues with Perf, and never claims the missing skill ran.

## Final status labels

| Status | Meaning |
| --- | --- |
| **VERIFIED** | Evidence covers all material requested criteria |
| **PARTIALLY VERIFIED** | Only some criteria are established |
| **BLOCKED** | A named dependency prevents the remaining useful work |
| **NOT VERIFIED** | Evidence does not establish the outcome |

Implementation completeness is reported separately. A finished artifact is not
proof of verification.

## Tips

- List acceptance criteria explicitly; Craft verifies against them.
- Say which checks may run (tests, browser, integration). Unavailable tools are
  reported as unrun, never as passes.
- Craft is instruction loading, not a runtime. Native delegation is used only
  when the host supports it and it is authorized.

## Related

- [Design and evaluation of Craft](../panda-craft.md)
- [Lead](panda-lead.md), [Buddhist Method](buddhist-method.md)
