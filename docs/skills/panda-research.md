# Panda Research

Panda Research resolves a bounded technical question with traceable evidence:
repository source, official documentation, specifications, and original papers.
Use it when evidence gathering is the main task. Every other skill still gathers
ordinary evidence on its own.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Verifying a technical claim, checking version support, comparing libraries or capabilities against criteria |
| **Not for** | Exploring a direction ([Brainstorm](panda-brainstorm.md)), diagnosing a failure ([Debugger](panda-debugger.md)), tracing a proposed change ([Impact](panda-impact.md)), writing a guide ([Write](panda-write.md)) |
| **Edits by default** | None, apart from a research note you request |
| **Main output** | A direct answer, claim-level citations, versions and dates, uncertainty, decision implications |

## How it works

1. **Bound the question.** Identify the claims or comparison criteria, the
   versions and environments, and what evidence would answer them. Effort scales
   with the decision.
2. **Gather primary evidence.** Source, configuration, tests, official docs,
   specifications, papers. Search results and blog summaries are leads; the
   underlying source is inspected before it is relied on. Changing facts are
   checked against current authoritative sources with dates recorded.
3. **Test the premise.** Documented support, implementation, test coverage, and
   observed runtime behavior are kept distinct. Conflicting evidence is weighed
   by authority, version, environment, and method. Repeated copies of one claim
   are not independent corroboration. "Not found" is bounded by what was searched.
4. **Synthesize.** Claim-level citations (file paths and symbols for repository
   evidence, links and sections for external sources). Verified findings,
   inference, assumptions, and unknowns are separated.
5. **Check completion.** Each deciding claim has evidence or an explicit gap. If
   the deciding evidence is unavailable, you get a bounded conclusion and the
   smallest missing check.

## What to provide

- The question and the decision it informs.
- Relevant paths, URLs, and the versions you actually run.
- Whether you want a saved note (and where), or a chat answer.

## Examples

### Version support check

```text
$panda-research Check whether the SDK version pinned in this repository supports
our required authentication flow. Compare implementation and official versioned
documentation. Cite deciding claims, explain contradictions and unknowns, and
save docs/auth-research.md. Do not change code or install dependencies.
```

### Library comparison against criteria

```text
$panda-research Compare two PDF generation libraries for our Node 20 service.
Criteria: Thai font support, streaming output, license, and maintenance activity.
Use official docs and repositories, with dates. Recommend one and say what would
change the recommendation.
```

### Verify a claim before it goes in release notes

```text
$panda-research Is it true that our retry wrapper in src/http/retry.ts is
idempotency-safe for POST requests? Use the source and tests as evidence.
```

Expect implementation evidence and test coverage reported separately from any
documented intent.

### Standards question

```text
$panda-research Does RFC 9110 allow a 202 response for a PUT that is processed
asynchronously? Quote only the deciding section briefly and link it.
```

### Bounded "does this exist?" search

```text
$panda-research Does anything in this repository call the legacy /v1/orders
endpoint? Report what you searched and what remains unsearched (other repos,
external clients).
```

A negative finding is stated as "not found in the searched scope", never as
universal absence.

### Paper or algorithm check

```text
$panda-research Our rate limiter claims to implement GCRA. Compare
src/limits/gcra.go with the original algorithm description and list deviations.
```

### Freshness-sensitive question

```text
$panda-research What is the current LTS version of Node.js and when does our
pinned version reach end of life? Include the date you checked.
```

### Short answer only

```text
$panda-research Does PostgreSQL 16 support MERGE ... RETURNING? One paragraph,
with the doc link.
```

## Boundaries

Research is read-only by default. Source changes, dependency installation,
deployments, publication, paid experiments, and sharing data externally need
authorization covering them. Source content is treated as evidence, never as
instructions that grant permission.

## Related

- [Design and verification notes](../panda-research.md)
- [Learn](panda-learn.md) for understanding a codebase rather than answering one question
