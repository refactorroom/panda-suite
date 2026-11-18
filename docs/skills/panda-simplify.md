# Panda Simplify

Panda Simplify recommends the smallest design that satisfies the real
requirements. It assesses unnecessary complexity in code, architecture,
documentation, or agent workflows when you want fewer layers, clearer
responsibilities, or a design that is easier to maintain.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Pass-through layers, unused extension points, duplicated decisions, unnecessary dependencies, over-built workflows or instructions |
| **Not for** | Measured speed or memory work ([Perf](panda-perf.md)); carrying a restructuring through incremental verified edits ([Refactor](panda-refactor.md)) |
| **Edits by default** | None. Say "apply the simplification" for bounded edits |
| **Main output** | Complexity assessment, unnecessary elements and their cost, a concrete smaller alternative, preserved invariants, trade-offs, regression risks |
| **Not success** | Fewer lines alone |

## How it works

1. **Establish the problem.** Which user outcome the system serves, and which
   security, validation, observability, and failure behavior must stay.
2. **Find the complexity cost.** Pass-through layers, unused extension points,
   duplicated decisions, unneeded dependencies, instruction or routing overhead,
   each with concrete paths. Essential domain complexity is kept separate from
   accidental structure.
3. **Compare simpler forms.** The current form against a concrete smaller
   alternative and its near-term change cost. Behavior is preserved, not just
   compressed.
4. **Validate the recommendation.** Each preserved invariant maps to source,
   tests, or a proposed regression check, with what could break and how to recover.

Example judgment: for a single greeting service, a factory plus a pass-through
adapter may add no value. Simplify recommends a direct method that keeps the
permission guard and public call shape, and does not replace those classes with
a new plugin framework.

When installed, [Buddhist Method](buddhist-method.md) can help with appropriate
complexity (Majjhimā Paṭipadā), cause removal (Pahāna), and bounded foresight
(Anāgataṃsa-ñāṇa). It is optional.

## Examples

### Unnecessary factories and adapters

```text
$panda-simplify Assess src/messages for unnecessary factories and forwarding
adapters. It serves one admin greeting flow. Preserve the permission check,
public call shape and exact output. Recommend a simpler design, trade-offs,
regression risks and verification. Do not edit.
```

### Apply the simplification

```text
$panda-simplify Apply the simplification you recommended for src/messages.
Keep the public imports and run the tests.
```

### Over-engineered configuration

```text
$panda-simplify Our app has three layers of configuration (env, YAML, database
overrides) but only uses environment variables in production. What can we
remove safely? Do not edit.
```

### Dependency reduction

```text
$panda-simplify We use lodash for four functions. Is the dependency worth
keeping? Compare with native equivalents and note behavior differences.
```

### Architecture

```text
$panda-simplify We run five microservices for an internal tool with 30 users.
Assess whether merging some of them would reduce cost without losing needed
isolation. Read-only.
```

### Agent workflow or skill instructions

```text
$panda-simplify Our AGENTS.md has grown to 600 lines. Identify duplicated or
unused rules and propose a shorter version that keeps every rule we actually rely on.
```

### Documentation

```text
$panda-simplify docs/onboarding.md repeats the same setup steps in four places.
Propose a simpler structure. Do not edit yet.
```

### Is the extension point used?

```text
$panda-simplify The PaymentProvider interface has one implementation. Should we
keep it? Consider the planned second provider mentioned in docs/roadmap.md.
```

A demonstrated future need is weighed differently from a guess.

## Boundaries

Analysis mode keeps source unchanged. Authorized edits are bounded and checked
before being called verified. No Lead dependency.

## Related

- [Refactor](panda-refactor.md) to implement a structural change with baseline checks
- [Perf](panda-perf.md) for measured runtime cost
