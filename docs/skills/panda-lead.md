# Panda Lead

Panda Lead selects the smallest workflow that delivers your requested outcome.
It coordinates; each specialist keeps its own method. Use it when a request spans
several activities (discovery, planning, implementation, review, documentation)
or when you are not sure which skill fits.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Compound requests, workflow choice, carrying context and authorization between activities |
| **Not needed for** | A focused explanation, a tiny edit, or a task where you already know the specialist |
| **Edits by default** | Only what the selected specialists are authorized to do |
| **Main output** | Delivered artifacts plus an accurate status: implemented, verified, partially verified, blocked, or not started |
| **Requires** | Nothing else; missing specialists are reported, never simulated |

## How Lead decides

1. **Reads the request.** Lead identifies the outcome you want, the evidence
   available, your constraints, and the authorization you already gave. It
   inspects current artifacts before asking you for information. It matches the
   deliverable to your intent: an idea request gets exploration or a
   recommendation, not a finished artifact.
2. **Respects a named specialist.** If you name a skill, Lead uses it. Otherwise
   it routes by the artifact you want, not by a keyword in your prompt.
3. **Loads only what it needs.** Lead reads the selected skill through the host's
   discovery mechanism. Reading instructions is not a separate program running.
   If a skill is absent, Lead says so and explains what ordinary help it can
   still give.
4. **Orders dependent work.** A feature build may need plan, then execute. An
   approved plan needs only execute. Review and documentation are added when you
   ask for them or the project's acceptance criteria require them. Lead carries a
   compact [handoff](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-lead/references/handoff.md)
   between activities.
5. **Reports honestly.** Lead compares the delivered work and actual checks with
   your requested outcome and names remaining decisions or risks.

## Routing table

| You want | Lead selects |
| --- | --- |
| Compose named specialists under one shared outcome | [Craft](panda-craft.md) |
| Explore an idea, assumptions, alternatives | [Brainstorm](panda-brainstorm.md) |
| Investigate a technical question or verify a claim | [Research](panda-research.md) |
| Learn an unfamiliar codebase | [Learn](panda-learn.md) |
| Logos and visual identity | [Logo](../panda-logo.md) |
| Business rules, actors, acceptance | [Requirements](panda-requirements.md) |
| Tests: design, add, run, assess | [Test](panda-test.md) |
| What a proposed change could break | [Impact](panda-impact.md) |
| Release readiness | [Release](panda-release.md) |
| Commits, conflicts, history | [Git](panda-git.md) |
| Create or evaluate Agent Skills | [Skill Lab](panda-skill-lab.md) |
| Initialize or prepare a project | [Setup](panda-setup.md) |
| Ordered implementation tasks | [Plan](panda-plan.md) |
| Implement authorized work | [Execute](panda-execute.md) |
| Diagnose unexpected behavior | [Debugger](panda-debugger.md) |
| Performance and memory | [Perf](panda-perf.md) |
| Dedicated security audit | [Security](panda-security.md) |
| Surface mapping, telemetry, incidents, threat intelligence | [Recon](../panda-recon/README.md) |
| Defects in a change | [Review](panda-review.md) |
| Unnecessary complexity | [Simplify](panda-simplify.md) |
| Behavior-preserving restructuring | [Refactor](panda-refactor.md) |
| README, developer guide, runbook | [Write](panda-write.md) |
| Technical contract or design spec | [Spec](panda-spec.md) |
| User journey instructions | [Manual](panda-manual.md) |

[Buddhist Method](buddhist-method.md) is used only at a specific uncertainty,
repeated failure, pressure point, or complexity decision, never as a stage
between every activity.

Some overlaps are settled by rule: Requirements define *what*, Plan orders the
work, Impact traces what may break. Test owns test effectiveness; Debugger owns
causal investigation. Release preparation never implies deployment. Security
handles dedicated audits while Review handles ordinary changed-code defects.

## What to provide

- The outcome you want and how you will judge it.
- Relevant files, plans, URLs, or issue text.
- Constraints such as compatibility promises or areas not to touch.
- What may change: nothing, documents only, local code and tests, or more.

## Examples

### Full feature delivery from an approved plan

```text
$panda-lead Implement the approved feature in docs/approval-plan.md, review the
change, add meaningful tests, and prepare release notes. Local code and docs may
change. Do not deploy, publish, push tags, or change production data.
```

Expect execute, review, test, and release-preparation evidence in that order,
with no deployment. Planning is skipped because the plan already exists.

### Read-only explanation

```text
$panda-lead Explain how authentication works in this project.
Use the source as evidence. Do not change files.
```

A simple question can be answered directly. Lead may route to Learn for a
guided walkthrough, but it will not edit anything.

### From a vague idea to a plan, stopping before code

```text
$panda-lead Customers keep asking for scheduled exports. Help me decide whether
we should build it, then turn the chosen direction into requirements and a plan.
Do not implement anything.
```

Expect brainstorm output with a recommendation, then requirements and a saved
plan. Lead stops at the plan because implementation was not authorized.

### Bug report to verified fix

```text
$panda-lead Users report that saving a draft sometimes loses attachments.
Investigate and fix it, add a regression test, and write a short commit message.
Do not commit or push.
```

"Investigate and fix" authorizes the repair, so Debugger's fix proposal does not
need a second approval. Expect a confirmed cause, the fix, an executed
regression test, and a proposed commit message only.

### Change assessment before a risky migration

```text
$panda-lead We plan to split the users table into users and profiles. Tell me
what breaks, then plan the migration with release gates. Read-only except for the
saved plan.
```

Expect an Impact assessment followed by a Plan with release gates marked
"defined; evidence pending".

### Choosing a workflow only

```text
$panda-lead I need to make our CSV import faster and also easier to maintain.
Which Panda skills should handle this and in what order? Do not start the work.
```

Expect a short routing recommendation (for example Perf for measured cost and
Refactor or Simplify for structure) with reasons, and no work started.

### Narrowing an earlier request

```text
$panda-lead Change of plan: only review the current diff. Do not run the
release preparation we discussed earlier.
```

A new request can narrow earlier scope. Lead identifies the current outcome and
carries forward only the evidence and authorization that still apply.

## Authorization rules

- Investigation, planning, review, and recommendations do not authorize source
  changes.
- An explicit implementation request authorizes relevant reversible edits, and
  Lead carries that permission forward without asking again.
- Destructive operations, publication, deployment, production changes, and
  external side effects need authorization that covers those actions.

## Tips

- Say what "done" means. Lead compares the result with it.
- Name a specialist if you already know it; Lead will not override you.
- You do not need Lead to use any other skill. Every specialist works alone.

## Related

- [Workflows and routing](../routing.md)
- [Craft](panda-craft.md) for explicit composition of named specialists
- [Routing decisions reference](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-lead/references/routing.md)
