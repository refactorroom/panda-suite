# Panda Skill Lab

Panda Skill Lab creates, reviews, evaluates, and improves Agent Skills. It asks
whether skill instructions solve a distinct problem and improve real work, and it
answers with controlled evidence rather than impressions.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | A skill with an observed failure, unclear routing, host compatibility questions, context overhead, or a proposed new skill |
| **Not for** | Ordinary application features, explanations, or one-off debugging |
| **Edits by default** | Creation requests authorize the scoped skill; review and evaluation requests do not authorize edits |
| **Main output** | Purpose, failure mode, contract, scenarios, actual baseline and skill results, comparison, weaknesses, next improvements |
| **Never** | Simulated baselines, invented benchmarks, or token-savings claims from word counts |

## How it works

1. **Define the problem.** What normal agent behavior gets wrong, why it
   matters, and observable success criteria. A hypothesized failure is kept
   separate from an observed one. Current instructions are inspected first: a
   recorded defect may already have a correction worth evaluating.
2. **Define the contract.** Name, trigger description, non-triggers, inputs,
   workflow, outputs, permission boundaries, evaluation criteria. The format is
   checked against the [Agent Skills specification](https://agentskills.io/specification)
   and the target host's discovery. Valid format proves neither compatibility nor behavior.
3. **Design minimally.** Concise, independently usable instructions;
   skill-local references only for conditional detail; upstream attribution kept.
4. **Create blind cases.** Normal use, missing information, conflicting
   evidence, ambiguity, tool failure, wrong assumptions, authorization,
   out-of-scope pressure, and a case where the skill should **not** activate.
   Answer keys stay away from the task-performing agent.
5. **Run baseline and skill arms.** Fresh contexts per case and arm, with the
   same model settings, tools, inputs, and budget. Without a runner, Skill Lab
   delivers runnable scenarios and marks the comparison **Not Run**.
6. **Compare and diagnose.** Correctness, evidence, usefulness, scope,
   verification honesty, overhead. Instruction defects are separated from
   missing evidence, host limits, and model variance.
7. **Improve and regress.** Only demonstrated weaknesses are changed, then the
   relevant checks (including non-activation) are repeated. A skill that adds no
   observed value can be simplified, merged, or removed.

## Examples

### Evaluate a specific failure mode

```text
$panda-skill-lab Evaluate whether panda-plan catches contradictions between
proposed signatures and promised errors. First inspect existing coverage. Design
blind baseline and skill cases with identical inputs, tools and model settings,
fresh contexts per arm, and nonactivation/scope cases. If no runner is available,
deliver the protocol and mark comparisons Not Run. Do not edit skills yet.
```

### Create a new skill

```text
$panda-skill-lab Create a skill for writing database migration reviews in our
team's format. Check first whether an existing skill already covers it. Include
non-triggers and three evaluation cases.
```

### Review a skill's description and routing

```text
$panda-skill-lab Review skills/panda-perf/SKILL.md. Would its description
trigger for "the page is slow" and not for "explain this function"? Propose
wording changes with reasons. Do not edit.
```

### Host compatibility

```text
$panda-skill-lab Check whether our skills directory is discovered correctly by
Codex and Claude Code. Report what was actually observed and what remains untested.
```

### Reduce context overhead

```text
$panda-skill-lab panda-security's SKILL.md feels long. Identify instructions that
duplicate global rules or could move to a conditional reference, without losing
behavior. Do not claim token savings without measurement.
```

### Contract-verification fixture

```text
$panda-skill-lab Build a fixture where the test suite passes but a stated
requirement is violated, plus a correct control. Validate the fixture locally.
```

Validating the fixture proves the case discriminates; it does not prove the model
behaves better.

### Improve after an observed failure

```text
$panda-skill-lab In tests/results/run-42 the review skill invented a finding.
Diagnose whether it is an instruction defect, then propose the smallest change
and the regression case that would catch it.
```

### Should this skill exist?

```text
$panda-skill-lab Do we need a separate panda-migration skill, or do Plan and
Impact already cover it? Base the answer on existing coverage.
```

## Boundaries

Publishing, installing into global configuration, sharing data externally, and
production actions need authorization. [Buddhist Method](buddhist-method.md) is
an optional aid at a specific uncertainty, not a stage in every evaluation.

## Related

- [Evaluation instructions](../../tests/evaluation.md)
- [Extend the suite](../skill-contract.md)
- [Evaris](panda-evaris.md) for running structured agent and skill evaluations
