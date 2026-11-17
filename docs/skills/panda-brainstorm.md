# Panda Brainstorm

Panda Brainstorm turns an idea into an evidence-based direction. Use it when the
problem, the constraints, the assumptions, or the choice of approach still needs
clarifying before anyone commits to a solution.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Undecided direction, comparing approaches, challenging assumptions |
| **Not for** | An agreed plan (use [Plan](panda-plan.md)), testable business rules ([Requirements](panda-requirements.md)), a code explanation |
| **Edits by default** | None. Brainstorming is analysis |
| **Main output** | Problem statement, goals/non-goals, assumptions, alternatives, trade-offs, recommendation, risks, open decisions |
| **Valid result** | "Keep the current approach" or "do less" |

## How it works

1. **Understand the goal.** Who has the problem, what task they struggle with,
   and which outcome would matter. A proposed solution ("a microservice") is kept
   separate from the need ("managers need faster decisions").
2. **Identify constraints.** Current behavior, goals and non-goals, existing
   capabilities, operational limits, business and UX obligations.
3. **Challenge assumptions.** Each material premise is marked supported,
   assumed, or unknown, with the smallest experiment that could change the
   decision. Your confidence is not treated as technical evidence.
4. **Explore alternatives.** Extending the current system and doing less are
   always considered when viable. Options are compared only on dimensions that
   distinguish them. No invented cost or time estimates.
5. **Recommend.** The recommendation is tied to the goal and the strongest
   constraints, with its trade-offs and the condition that would favor another
   option. With weak evidence, the recommendation is a bounded discovery step.

If you challenge a suggestion, Brainstorm reassesses the premise and the deciding
evidence before proposing a replacement.

## What to provide

- The user problem and who has it.
- Existing system context (paths to inspect) and constraints such as budget,
  team size, or deadlines you actually have.
- Whether you want options only, or a recommendation.

## Examples

### Compare two architectures

```text
$panda-brainstorm Our five-person support team approves refunds manually.
Compare extending the existing admin application with a separate approval service.
Inspect src/refunds first. Recommend a direction with assumptions and trade-offs.
Do not implement or create an execution plan.
```

### Should we build this at all?

```text
$panda-brainstorm Sales wants a "dark mode" for the admin panel. Ten internal
users use it. Is it worth doing now? Consider doing nothing and cheaper options.
```

Expect "do nothing" or a minimal option to be weighed seriously.

### Explore without choosing

```text
$panda-brainstorm Give me three different ways to let customers schedule
exports. Do not recommend one yet; list what evidence would decide between them.
```

### Challenge an assumption

```text
$panda-brainstorm The team believes search is slow because of the database.
Which assumptions behind that belief are supported by src/search and which are
not? What is the smallest experiment that would settle it?
```

### Product direction with a hard constraint

```text
$panda-brainstorm We must support offline field data entry on tablets, and we
have no mobile developers. What realistic approaches exist using our current
React web app? Mark each premise supported, assumed, or unknown.
```

### Reassess after pushback

```text
$panda-brainstorm You recommended a queue for notifications. We already run
cron jobs every minute. Does that change your recommendation?
```

Expect a reassessment of the premise ("do we need a queue?") against the new
evidence, not a reflexive replacement.

### Small idea, short answer

```text
$panda-brainstorm Should our CLI print JSON by default or only with --json?
Two paragraphs are enough.
```

Output length scales with the decision.

### Hand off to the next step

```text
$panda-brainstorm Help me pick a direction for multi-tenant billing. Once I
agree, turn the chosen direction into requirements with panda-requirements.
```

When a later activity is requested, the handoff carries the direction,
constraints, evidence, open decisions, and authorization.

## Boundaries

Brainstorm does not implement, change source, run experiments with side effects,
or write an execution plan unless you ask. It works without Lead or any other
installed skill.

## Related

- [Requirements](panda-requirements.md) for testable rules once direction is set
- [Research](panda-research.md) to verify a single technical claim
- [Impact](panda-impact.md) to trace what a chosen change would affect
