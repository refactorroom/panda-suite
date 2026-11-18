# Panda Requirements

Panda Requirements defines what the system must accomplish before anyone chooses
how to build it. It refines business requests and stakeholder expectations into
testable requirements when actors, permissions, workflow rules, acceptance, or
scope are incomplete or in conflict.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Turning a request into testable rules, finding conflicts and missing decisions |
| **Not for** | Ordered engineering tasks ([Plan](panda-plan.md)), agreed technical contracts ([Spec](panda-spec.md)), a clear small change |
| **Edits by default** | Only the requested requirements document |
| **Main output** | A Requirements Analysis: goal, scope, actors and permissions, functional requirements with IDs, business rules, relevant quality requirements, acceptance criteria, edge cases, open questions |
| **Never does** | Choose stakeholder policy for you, or invent targets such as an uptime percentage |

## How it works

1. **Understand the problem.** Business goal, stakeholders, actors, current and
   desired workflow, constraints, scope, and non-goals. The underlying need is
   kept separate from a suggested feature.
2. **Classify premises.** Confirmed requirements carry their source.
   Assumptions, proposals, conflicts, and missing information stay distinct.
   Conflicting stakeholder requests are never silently resolved.
3. **Analyze rules.** Permissions, states and transitions, ordering, required
   and optional data, validation, exceptions, failures, external dependencies,
   and duplicate or concurrent actions when relevant. Existing code shows current
   behavior, not stakeholder approval of it.
4. **Define functional requirements.** Each has a stable ID, description,
   actor/component, expected behavior, constraints, and acceptance criteria.
   Related rules are grouped rather than inflated.
5. **Define relevant quality requirements.** Security, reliability, audit,
   accessibility, performance, retention, and maintainability only where the
   outcome needs them. A missing target is recorded as a decision.
6. **Check acceptance and completeness.** Observable statements (Given/When/Then
   is optional) cover actors, denied operations, state boundaries, invalid data,
   and failures. Every open material rule states its impact and whether it
   blocks planning.

## What to provide

- The stakeholder request (document, ticket, or text).
- Current workflow and the code area that implements it today.
- Known policy, and which decisions are still open.

## Examples

### Multi-approval workflow with open policy

```text
$panda-requirements Refine docs/customer-request.md into requirements for multiple
approvals. Inspect the existing service. Ordering, quorum, self-approval and edit
invalidation are undecided. Give identified requirements, permissions, acceptance
criteria, conflicts and open decisions. Do not choose those policies or implement.
```

### Conflicting stakeholders

```text
$panda-requirements Finance wants refunds above 500 USD to need two approvals.
Support wants any refund under 24 hours old to be instant. Write requirements
that preserve both requests, show where they conflict, and name who must decide.
```

Expect both sources preserved and the conflict stated, not resolved.

### From a one-line ticket

```text
$panda-requirements Ticket: "Let admins deactivate users." Identify actors,
states, what happens to a deactivated user's sessions, API tokens and owned
records, and list each question that changes acceptance.
```

### Given/When/Then acceptance

```text
$panda-requirements Write acceptance criteria in Given/When/Then form for
password reset, covering expired links, reused links and unknown emails.
Use src/auth/reset.py for current behavior.
```

### Quality requirements without invented numbers

```text
$panda-requirements Add the relevant non-functional requirements for the
export feature. We have no agreed latency target or retention period yet.
```

Missing targets become explicit decisions, never made-up numbers.

### Edge cases for an existing rule

```text
$panda-requirements Our order cancellation rule says "only before shipping".
List the edge cases (partial shipments, concurrent cancel and ship, duplicate
requests) and the decision each one needs.
```

### Save and hand off to planning

```text
$panda-requirements Refine the scheduled-export request into
docs/export-requirements.md. When the open decisions are answered, hand the IDs
to panda-plan.
```

A handoff to Plan carries the IDs, sources, constraints, decisions, unknowns,
and actual authorization.

## Boundaries

Requirements analysis authorizes its requested document, not code changes, data
migration, or stakeholder decisions. It works independently with no master skill.

## Related

- [Brainstorm](panda-brainstorm.md) when the direction itself is still open
- [Plan](panda-plan.md) to order the work once rules are agreed
