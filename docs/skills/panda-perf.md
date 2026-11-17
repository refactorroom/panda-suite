# Panda Perf

Panda Perf finds the work that actually limits performance or memory and
proposes the smallest behavior-preserving optimization. It covers algorithmic
complexity, memory retention, redundant queries and N+1 patterns, and query
plans, and it validates both behavior and resource trade-offs.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Slow endpoints or jobs, high memory, N+1 queries, query plans, optimization diffs |
| **Not for** | Unexplained functional failures ([Debugger](panda-debugger.md)), structural cleanup ([Simplify](panda-simplify.md)), general diff review ([Review](panda-review.md)) |
| **Edits by default** | Analysis is read-only. "Give me a diff" yields a proposed patch; "optimize it" authorizes local changes |
| **Confidence labels** | Measured, Code-supported, Hypothesis |
| **Golden rule** | A faster wrong result fails |

## How it works

1. **Bound and reproduce.** Cost dimensions: CPU, wall time, allocations,
   retained memory, I/O, query count and rows, locks. Reported symptoms are kept
   apart from actual reproduction.
2. **Establish a baseline.** Existing profilers or a disposable harness. Revision,
   runtime, input size, warm-up, repetitions, cache state, and concurrency are
   recorded. One microbenchmark proves nothing about an SLO.
3. **Trace cost.** Complexity with defined variables; hot paths from profiles
   when available. For memory: owners, lifetimes, growth across repeated work.
   High RSS alone does not prove a leak.
4. **Inspect data access.** ORM lazy loads, query counts, predicates, joins,
   pagination, indexes, and actual plans. A sequential scan can be correct.
   Batching must preserve tenant filters, ordering, duplicates, nulls, and
   transaction semantics.
5. **Optimize concretely.** Bottlenecks ranked by supported cost. A minimal
   unified diff anchored to inspected code. No speculative caches, parallelism,
   or indexes when a local algorithm change is enough.
6. **Verify equivalence and cost.** The delivered diff is checked against a
   disposable copy (for example `git apply --check`), behavior checks run, and
   before/after measurements are repeated. Unfavorable samples are kept.
   Unverified patches are labeled Proposed/Unverified.

## What to provide

- The slow operation and how slow it is (or how much memory it uses).
- Workload sizes and distribution, runtime and version.
- Any profiles, query logs, or `EXPLAIN` output you have.
- Whether you want analysis, a proposed diff, or applied changes.

## Examples

### Repeated lookups and memory retention

```text
$panda-perf Analyze src/events.py for repeated lookups and memory retention.
Produce a minimal optimization diff preserving order, duplicates and permissions.
Run safe local equivalence and repeated synthetic comparisons; label missing
production evidence. Do not apply the patch or change database schema.
```

### N+1 queries in an endpoint

```text
$panda-perf GET /v1/orders takes 3 s for customers with 500 orders. Count the
queries per request with the local test database, confirm whether it is an N+1,
and propose a batched version that keeps tenant filtering and sort order.
```

### Query plan review

```text
$panda-perf Here is EXPLAIN ANALYZE output for the monthly report query
(attached). Is the sequential scan the bottleneck? Propose an index only if the
plan supports it. Do not change the database.
```

### Apply an optimization

```text
$panda-perf Optimize the CSV export in src/export/csv.py. It loads all rows into
memory. You may change that module and its tests. Show before/after peak memory
on a 200k-row synthetic file.
```

### Algorithmic complexity

```text
$panda-perf dedupe_contacts() in src/contacts/merge.py looks quadratic. Explain
the complexity with defined variables and propose a linear version that keeps
the first occurrence and original order.
```

### Memory growth in a worker

```text
$panda-perf Our queue worker's memory grows across jobs. Inspect src/worker for
retained objects and caches. Run 1,000 synthetic jobs locally and report growth
per job. Do not attach to production.
```

### Frontend rendering cost

```text
$panda-perf The product list re-renders every row on each keystroke in the
filter box. Find the cause in src/web/ProductList.tsx and propose a minimal diff.
```

### Static analysis only

```text
$panda-perf Without running anything, rank the likely hot spots in
src/pricing for a 10,000-item cart.
```

Findings are labeled Code-supported or Hypothesis, never Measured.

## Boundaries

Production profiling, load tests, dependency installation, database or index
changes, external workloads, and collecting or sharing sensitive traces need
authorization covering them. Planner cost estimates are never reported as
elapsed milliseconds.

## Related

- [Profiling and query guidance](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-perf/references/profiling.md)
- [Refactor](panda-refactor.md) when the goal is structure rather than speed
