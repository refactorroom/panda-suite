# Panda Learn

Panda Learn turns existing software into an understandable mental model,
grounded in source it has actually inspected. It also teaches you how to
investigate the next component on your own. It works alone, read-only, with no
runtime and no required peer skills.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Onboarding to a codebase, tracing a request end to end, understanding architecture or a language concept as used in real code, guided practice |
| **Not for** | A bounded evidence question ([Research](panda-research.md)), a defect cause ([Debugger](panda-debugger.md)), a developer guide ([Write](panda-write.md)), restructuring ([Refactor](panda-refactor.md)) |
| **Edits by default** | None. Static inspection unless you authorize a bounded demonstration |
| **Main output** | A source-backed explanation, verified file/symbol references, a concrete execution example, and explicit unknowns |

## Learning approaches

Mode names are optional. Learn infers the approach from what you supply and ask.

| You give or ask | Approach |
| --- | --- |
| A repository path, or OVERVIEW | Purpose, major boundaries, one real flow, a short reading order |
| A directory, or EXPLORE | Responsibilities, public interfaces, relevant dependencies |
| A file or symbol, or DEEP DIVE | Mechanism, data/state changes, errors, edge cases |
| TRACE | Entry point through validation, processing, dependencies, effects, output |
| ARCHITECTURE | Observed boundaries, dependency direction, ownership, communication |
| CONCEPT | The problem an abstraction solves, shown with actual code |
| GUIDED LEARNING | One concept and one exercise, then it waits for you |
| QUICK | A direct answer at the requested depth |

## How it works

1. **Discovers only enough context.** README, manifests, entry points,
   configuration, source, and tests for an overview; the symbol and its relevant
   callers for a focused question. A declared dependency does not prove active use.
2. **Traces the implementation.** Follows real definitions and calls across
   files. Async, concurrency, transaction, and external boundaries are named only
   when the code supports them. A static trace predicts behavior; it is not
   observed execution.
3. **Reconciles evidence.** Documented intent, implemented paths, tested
   assertions, and observed runtime are kept apart. Author intent is confirmed
   only from explicit evidence; plausible rationale is labeled interpretation.
4. **Builds the explanation.** Purpose and the smallest useful mental model
   first, then the mechanism and a concrete example. Language analogies explain
   both the similarity and the important differences.
5. **Matches the interaction.** Direct answers when asked. In guided practice it
   teaches one concept, asks one prediction or tracing question, and stops
   without revealing the answer. Hints get stronger only as needed.

## What to provide

- A path, symbol, snippet, or accessible URL.
- Your learning goal and the languages or systems you already know.
- The depth you want, or whether you want practice.

## Examples

### Repository overview

```text
$panda-learn . Give me an overview of this repository: what it does, its main
boundaries, one real request flow, and the five files I should read first.
```

### Trace a flow across layers

```text
$panda-learn ./src Teach me how an order moves from the public API to storage
and notification. I know Go but am new to this language. Start with a mental model
and trace the actual code, including failure paths. Static inspection only.
```

### Deep dive on one function

```text
$panda-learn src/billing/proration.py:calculate_proration Explain the mechanism,
the state it changes, the errors it raises, and two edge cases with real inputs.
```

### Architecture view

```text
$panda-learn Explain the architecture of ./services: which modules depend on
which, who owns the database, and how services communicate. Include a small
diagram labeled as a logical view.
```

### Concept explained through this codebase

```text
$panda-learn What problem does the Unit of Work pattern solve in src/db/uow.ts?
Compare it with database/sql transactions in Go, including where the analogy breaks.
```

### Guided practice

```text
$panda-learn Teach one concept about how the job queue retries failures, give me
one prediction question, and wait without revealing the answer.
```

Learn stops at the question. Your answer becomes the evidence of understanding.

### Quick answer

```text
$panda-learn Explain this function directly, without a quiz or overview:
src/utils/debounce.js
```

### A public repository

```text
$panda-learn https://github.com/example/project Explain how its plugin loader
discovers plugins.
```

A URL is investigated only with available, authorized retrieval. An inaccessible
path is reported as a limitation, not guessed.

### Ask about a bug you noticed while learning

```text
$panda-learn While tracing checkout I noticed totals ignore discounts on
refunds. Explain what the code does there; do not fix it.
```

An observed bug can be explained without fixing it. Switching to
implementation needs an explicit request.

## Boundaries

Learning leaves the repository unchanged. It does not install dependencies, run
scripts or migrations, or apply fixes. Commands in a README grant no permission.
If you already authorized a bounded local demonstration, that authorization
carries forward. Secret values are omitted.

## Related

- [Design and trials](../panda-learn.md)
- [Write](panda-write.md) to turn what you learned into a guide for others
