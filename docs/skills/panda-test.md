# Panda Test

Panda Test verifies behavior and invariants with useful tests, not with a
higher test count. It designs, adds, runs, or assesses unit, integration, API,
regression, and end-to-end tests when behavior needs proof or existing coverage
may miss real failures.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Regression tests, coverage gap analysis, choosing test levels, judging whether assertions would catch a defect |
| **Not for** | Finding a defect's cause ([Debugger](panda-debugger.md)) |
| **Edits by default** | Analysis is read-only. "Create tests" authorizes test and fixture changes, never unrelated production fixes |
| **Main output** | Scope, scenarios, test files, actual execution results, coverage gaps, risks |
| **Honesty rule** | Proposed tests are **Not Run** until executed; a mock never counts as an integration pass |

## Choosing the test level

| Level | Use for |
| --- | --- |
| Unit | Isolated rules and calculations |
| Integration | Real interactions between components (database, queue) |
| API | Request/response contracts |
| End-to-end | A complete user journey |

Test avoids proving the same thing at every layer and states which real
dependencies or mocks each level needs.

## How it works

1. **Understand behavior.** Requirements map to inputs, outcomes, permissions,
   state transitions, errors, and invariants. Assertions are read, not just test
   names: a green suite can miss a stated requirement.
2. **Choose boundaries** from the table above.
3. **Design cases** for real risks: normal behavior, invalid or missing data,
   boundaries, dependency or transaction failure, authorization, concurrency,
   duplicates, idempotency. A reported defect gets a discriminating regression case.
4. **Implement authorized tests** with the repository's framework and fixtures.
   Assertions check observable outcomes, including unchanged state on failure.
5. **Execute** and record exact commands, environment, exit status, and failures.
6. **Assess effectiveness.** Assertions, boundary data, isolation, brittleness,
   unnecessary mocks, flakiness. Where safe, it shows the regression fails against
   the faulty behavior. Tests are never weakened to hide a failure.

## Examples

### Regression tests for a permission rule

```text
$panda-test Add regression tests for owner-only cancellation in src/orders.py.
Use existing unittest conventions. Cover owner success, non-owner rejection,
shipped orders and unchanged state on failure. Run them. You may change tests
and local fixtures; do not modify application code to make a failing test pass.
```

A discovered defect can produce a useful failing test; Test reports it rather
than patching the code.

### Coverage gap analysis (read-only)

```text
$panda-test Assess whether tests/payments cover the refund rules in
docs/refund-requirements.md. List requirements no assertion would catch.
Do not write tests.
```

### Would the tests catch this bug?

```text
$panda-test If someone removed the tenant filter in src/reports/query.py, would
any test fail? Show the evidence and propose the smallest discriminating test.
```

### Integration test with a real database

```text
$panda-test Add an integration test for the order repository using the local
Postgres from docker-compose.yml. If the database is not available, say so and
do not replace it with a mock.
```

An unavailable database means the integration check is **Not Run**.

### API contract tests

```text
$panda-test Write API tests for GET /v1/invoices covering pagination, an
unknown tenant, an expired token, and an empty result. Run them against the
local test server.
```

### End-to-end journey

```text
$panda-test Add one end-to-end test for sign-up through first project creation
using the existing Playwright setup. Use synthetic data only.
```

### Flaky test investigation

```text
$panda-test tests/test_scheduler.py::test_runs_once fails about one run in
twenty. Assess why it is flaky and propose a deterministic version. Do not
change application code.
```

### Test strategy for a new feature

```text
$panda-test Propose a test strategy for bulk CSV import from the plan in
.panda-suite/plans/2026-11-12-bulk-csv-import.md. Say which level proves each
acceptance rule. Do not write tests yet.
```

## Boundaries

Production data, destructive testing, external side effects, and new
infrastructure need authorization covering them. If diagnosis is needed, Test
passes evidence to [Debugger](panda-debugger.md) when available, or reports the
unresolved defect and the smallest useful investigation.

## Related

- [Debugger](panda-debugger.md), [Review](panda-review.md), [Execute](panda-execute.md)
- [Practice locally](../usage.md#practice-locally) with an evaluation fixture
