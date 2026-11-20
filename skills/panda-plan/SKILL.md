---
name: panda-plan
description: Create engineering implementation plans from requirements and existing source when the user needs ordered tasks, dependencies, acceptance criteria, risks, and verification before execution; review and archive completed or explicitly superseded saved plans when asked to process them.
---

# Panda Plan

Turn agreed requirements into executable work. Explore unclear needs before
planning. For saved plan review or archival, follow [processed plans](references/processed-plans.md)
instead of drafting a new plan. A read-only review moves nothing; archive only
verified or explicitly superseded plans.

## Inputs and workflow

Use the requirements, repository, constraints, and requested scope. An existing
design or spec is optional. If source is unavailable, identify the affected
unknowns and label any proposed file layout as provisional.

1. **Requirements.** Capture intended behavior, non-goals, compatibility and
   mandatory acceptance conditions. Preserve requirement IDs or assign short IDs.
   Cite confirmed facts and label proposals, assumptions and open decisions.
   Resolve ambiguities that materially affect correctness or scope.
2. **Current system.** Inspect relevant source, callers, assertions, config and
   project instructions. Cite paths. Reuse existing capabilities and prefer the
   smallest design that meets the need.
3. **Contracts.** Identify affected interfaces, source of truth, ownership,
   invariants, dependencies and failure recovery. For public changes, specify
   compatibility checks, error semantics, versions and migrations. Include
   rollback and observability where warranted. Split independent subsystem plans
   while naming shared contracts and prerequisites.
4. **Tasks.** Order by actual dependencies. Each task has an ID, action title,
   outcome, requirement IDs, files/components, prerequisites, acceptance and checks.
   State changed/preserved behavior and relevant exclusions. Specify each consumed
   and produced interface with exact names, signatures, required values and
   compatibility rules. Match existing interfaces to source. Label new ones as
   proposed. Group setup, tests and docs with the behavior they support.
5. **Verification.** For each critical behavior, name a plausible wrong
   implementation and the assertion that detects it. Give test level, inputs,
   expected outcomes, fixtures, dependencies and relevant regressions. Inspect
   existing assertions for gaps. Confirm commands from repo tooling and label
   proposed commands or unavailable environments. Use test-first sequencing when
   helpful. Checks stay planned until run.
6. **Reconcile.** Trace each requirement through task, acceptance, check and
   expected evidence or explicit gap. Use a matrix only for complex work.
   Check for cycles, missing prerequisites and inconsistent interfaces or errors.
   Resolve placeholders or mark blockers. Specify omitted, null, empty and invalid
   inputs separately when semantics differ. Verify the framework can emit each
   promised error at that boundary. Give material risks checks, mitigations or
   open decisions. Apply scope changes across the entire artifact, including
   evidence, release gates and handoff. Search for and remove stale references.

## Output and completion

Save the plan as Markdown at `.panda-suite/plans/YYYY-MM-DD-<topic>.md`, using
the current local date and a short lowercase hyphenated topic. Create the directory
when needed. An explicit user-requested destination takes precedence. Avoid
overwriting an unrelated existing plan; choose a distinct descriptive filename.
When the user requests an answer only in chat, honor that format. If the workspace
cannot be written, provide the plan in the response and explain the limitation.

When saving under `.panda-suite` in Git, follow [saving plans](references/saving-plans.md) to verify ignore coverage and preserve tracked files and the index.

Start with title, goal, scope, source/specification and constraints, carrying
project-wide constraints with exact required values. Map affected files and
responsibilities, then ordered tasks with Markdown checkboxes for actionable work.
For substantial changes add a review focus: up to five likely implied but untested
inputs/failures, expected behavior, and the owning task's check; say when none
remain. A localized change can use one short task with its source, contract,
acceptance and checks inline, without separate matrices or ceremonial sections.
Write decisions and expected evidence, not implementation transcripts.

For a defined release, deployment, migration or compatibility boundary, read
[release gate planning](references/release-gates.md) and define proportional gates.
Otherwise omit release gates. Planning defines what must be verified;
`panda-release`, when requested and available, assesses the actual revision and
its evidence. `panda-execute` owns implementation and check execution; `panda-test`
owns separately requested test work. These skills are optional, not dependencies.

Before delivery apply step 6 and assess **plan readiness**:

- **EXECUTION-READY:** no unresolved decision blocks authorized implementation.
- **PARTIALLY READY:** name tasks that can start and decisions/prerequisites blocking others.
- **BLOCKED:** critical scope or contract decisions prevent execution.

Assess readiness across every task in the saved execution scope; name blocked
task IDs rather than labeling that entire scope ready. Name the first unblocked
task and any evidence gaps. An unavailable release
check may leave implementation ready while release evidence remains missing.
These labels do not assess release readiness; defined gates are not passed gates.
A task checkbox records completion only after its required acceptance checks
produce evidence. Link the saved plan and identify unresolved decisions/checks.
Saving a plan requires no commit.

When implementation is a relevant next step, follow [execution handoff](references/execution-handoff.md)
for the review request and mode choice. Planning alone authorizes no implementation.
