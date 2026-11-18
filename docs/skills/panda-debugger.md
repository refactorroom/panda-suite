# Panda Debugger

Panda Debugger investigates frontend and backend bugs in any language, using
the source, runtime, browser, log, and test evidence that is available.
**Understand the problem first. Prove the root cause. Propose the fix; edit only
when authorized.**

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Exceptions, failing tests, API errors, incidents, wrong output, UI behaving unexpectedly |
| **Not for** | Measured performance work ([Perf](panda-perf.md)), dedicated security audits ([Security](panda-security.md)) |
| **Edits by default** | None. "Investigate and fix" authorizes the repair in the same request |
| **Main output** | Root cause at a glance, causal trace, confidence, fix proposal, verification status, remaining risk |

## Confidence labels

| Label | When it is used |
| --- | --- |
| **CONFIRMED** | Evidence connects the mechanism to the observed failure (a focused experiment, or a complete observed trace backed by code) |
| **LIKELY** | A key causal check is still missing |
| **UNKNOWN** | Evidence is insufficient |

Reproducing a symptom alone does not confirm its cause.

## The six phases

1. **Understand.** Expected versus actual behavior, inputs, environment, onset,
   frequency, scope. Hypotheses stay hypotheses; no fix yet.
2. **Reproduce.** The smallest safe reproduction, with command, environment,
   and actual result. If it cannot run, Debugger says why. A static inference is
   never called an observed reproduction.
3. **Trace.** Data and control flow from input to failure, including
   validation, transformations, state, error handling, transactions, external
   calls, and concurrency. The failure location is distinguished from the origin.
4. **Identify root cause.** Each plausible explanation is tested against
   supporting and contradicting evidence. Primary cause is separated from
   contributing factors.
5. **Propose a fix and request approval.** The smallest change, affected files,
   why it addresses the cause, regression risks, and a verification plan. If you
   already asked to fix, that is the approval.
6. **Verify after implementation.** A regression test where meaningful, the
   original scenario, and relevant edge cases, each with the actual command and result.

## Tools it adapts to

Source search for static tracing, the project's test runner or debugger for
reproduction, a browser for UI behavior, and logs, traces, databases, or queues
for backend paths. No specific tool is required. A missing capability means the
check is **Not Run**, with the evidence gap explained.

## Examples

### Backend: success response, unchanged data

```text
$panda-debugger Investigate why transfer returns success but balances remain
unchanged. Inspect src/transfers and run the available local regression. Show the
causal trace, evidence and CONFIRMED/LIKELY/UNKNOWN confidence. Propose the smallest
fix and its verification. Do not edit application code or tests.
```

### Investigate and fix in one request

```text
$panda-debugger Investigate and fix the 500 error on PATCH /v1/profile when the
bio is empty. Add a regression test and run the suite.
```

No second approval is needed for that scope.

### Failing test

```text
$panda-debugger tests/test_tax.py::test_rounding started failing after the
currency library upgrade. Find the cause. Read-only.
```

### Frontend: stale results in the UI

```text
$panda-debugger The search page sometimes shows results for the previous query.
The app runs at http://127.0.0.1:5173. Observe it in the browser, trace
src/search, and explain the cause. Do not edit.
```

With browser access, Debugger observes the real page; without it, the browser
checks are reported as Not Run.

### From a stack trace

```text
$panda-debugger Here is a production stack trace (attached, secrets removed).
Map it to the code at commit 4f2a9c1 and explain the most likely cause and what
evidence would confirm it.
```

Production state is not assumed from local code; missing evidence is named.

### Intermittent or concurrency issue

```text
$panda-debugger Duplicate invoices appear about once a week. Inspect the invoice
job and its locking. List possible causes and the observation that would
distinguish them.
```

Expect separate **possible causes**, each with a deciding check, when evidence
does not single one out.

### Data/transaction boundary

```text
$panda-debugger Orders are marked paid but the payment row is missing. Trace the
transaction boundaries between src/orders and src/payments. Use the local test
database only.
```

### Ask for a flowchart

```text
$panda-debugger Explain why webhook retries create duplicate emails and include
a Mermaid flowchart of the execution path.
```

Diagrams show only evidence-backed steps, with inferred steps labeled.

## Report format

Reports use clear B2-level English and open with **Root cause at a glance**: one
sentence per cause with its confidence label, primary cause first. Substantial
investigations follow the
[report template](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-debugger/references/report-template.md).

## Boundaries

No destructive commands, production data changes, or external side effects
without authorization. Logs, locations, reproductions, and test results are
never invented.

## Related

- References: [investigation guide](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-debugger/references/investigation-guide.md),
  [frontend browser](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-debugger/references/frontend-browser.md),
  [backend evidence](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-debugger/references/backend-evidence.md)
- [Test](panda-test.md) for the regression suite, [Buddhist Method](buddhist-method.md) for stubborn failures
