# Panda Evaris

Panda Evaris designs and runs evidence-backed agent and skill evaluations with
Evaris: experiments, preparation of task workspaces, import of external results,
grading, reports, comparisons, and optional Invaris verification.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Comparing agents or skills (baseline versus specialist), grading imported runs, regression comparisons between revisions |
| **Not for** | A standalone project check ([Invaris](panda-invaris.md)), ordinary test design ([Test](panda-test.md)) |
| **Requires** | A compatible Evaris CLI to execute; real agent runs need a separate authorized host |
| **Edits by default** | Only within the requested experiment scope |
| **Key rule** | Reviewer material never reaches the task-performing agent |

## How it works

1. **Define the evaluation:** question, arms, cases, criteria, authorized
   actions, and comparable conditions. Existing configuration and fixtures are
   inspected first. The installed Evaris version and documentation are checked:
   features differ by version.
2. **Validate and prepare** separate workspaces. Evaris prepares tasks but does
   **not** launch the external agent. `.evaris/`, reviewer oracles, private
   configuration, evidence stores, and import requests stay away from task agents.
   Directory separation alone is not a security sandbox.
3. **Import actual results only:** responses and metadata observed for the
   matching case and arm. Missing values stay unknown; synthetic controls are
   labeled. Graders and their side effects are inspected before running.
4. **Compare** only through the tool's comparability result. A non-comparable or
   incomplete comparison establishes neither regression nor improvement.
   Correctness, evidence, scope, and overhead are reported separately.
5. **Optional Invaris verification** needs a matching harness profile, a
   supported evidence schema, an explicit executable, and permission. Evaris 0.4.0
   documents `check` (restricted `invaris.dev/v1alpha2` harness and
   `invaris.evidence/v1alpha2` evidence) and `campaign` (an
   `invaris.campaign/v1alpha1` file); earlier versions support `check` only.

## How verdicts combine

| Native Invaris verdict on a required check | Effect on the Evaris assessment |
| --- | --- |
| REJECT | Fails |
| REFUSE, ERROR, UNAVAILABLE | Inconclusive |
| ACCEPT | Cannot override failed or missing task criteria |

Native verification and the Evaris assessment are always reported separately.

## Examples

### Prepare a baseline versus specialist evaluation

```text
$panda-evaris Inspect my experiment, validate it, and prepare a baseline and
specialist evaluation. Keep reviewer evidence private; report what remains.
```

### Design a new experiment

```text
$panda-evaris Design an experiment comparing a plain agent with one using
panda-review on five diff-review cases, including one correct change that should
produce no findings. Do not run anything yet.
```

### Import external results

```text
$panda-evaris Import the agent outputs in runs/2026-11-15/ for case REV-03, arms
baseline and specialist. Keep missing model settings as unknown.
```

### Grade and report

```text
$panda-evaris Grade the imported results with the configured graders and write
the report. Inspect the graders' commands before enabling execution.
```

### Compare two skill revisions

```text
$panda-evaris Compare the results for panda-plan at commits a1b2c3d and HEAD.
Use Evaris's comparability result and say whether any difference is supported.
```

### Add Invaris verification

```text
$panda-evaris Add a restricted Invaris check to each case using the profile the
installed Evaris documents. Report Invaris verdicts separately from task grades.
```

### No runner available

```text
$panda-evaris Evaluate whether panda-debugger improves root-cause accuracy.
We have no automated agent runner.
```

Expect runnable cases and the behavioral comparison marked **Not Run**; no
simulated runs or improvement claims.

## Boundaries

Responses, executions, model settings, loaded instructions, and provenance are
never invented. Software is not installed without authorization. Effectiveness
is never claimed from configuration validity or synthetic controls alone.

## Related

- [Skill Lab](panda-skill-lab.md) for designing and improving skills
- [Invaris](panda-invaris.md)
- [Practice locally](../usage.md#practice-locally) with the suite's own evaluation fixtures
