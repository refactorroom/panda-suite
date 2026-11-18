---
name: panda-evaris
description: Design and run Evaris agent and skill evaluations, including experiments, external-result import, grading, reports, comparisons, and optional Invaris verification.
---

# Panda Evaris

Use Evaris for evidence-backed agent or skill evaluation. A standalone project
check is an Invaris task; ordinary test design does not require Evaris. This
skill works independently without Panda Lead or Invaris.

## Workflow

1. Define the evaluation question, arms, cases, criteria, authorized actions,
   and comparable conditions. Inspect existing experiment configuration,
   fixtures and outputs before changing them. Author or edit only within the
   requested scope. Check installed Evaris usage and matching documentation:
   versions differ, including availability of initialization. If a binary or
   feature is missing, report the limitation; do not invent results or install
   software without authorization.
2. Validate the configuration and prepare separate workspaces when requested
   and supported. Evaris prepares tasks but does not launch the external agent.
   Keep `.evaris/`, reviewer oracles, private configuration, evidence stores and
   import requests away from task-performing agents; give each agent only its
   assigned task workspace. Directory separation alone is not a security sandbox.
   Use fresh comparable contexts for each arm when available and authorized.
3. Import only actual external results and metadata observed for the matching
   prepared case and arm. Preserve missing values as unknown; identify authored
   synthetic controls as such. Do not invent agent responses, execution, model
   settings, loaded instructions or provenance. Inspect configured graders and
   side effects before running; enable command execution only within authorized
   scope. Evaluate and report actual evidence and limitations.
4. Compare arms or revisions only using the tool's comparability result. A
   non-comparable or incomplete comparison does not establish a regression or
   improvement. Separate correctness, evidence, scope and overhead; do not
   claim effectiveness from configuration validity or synthetic controls alone.
5. Optional Invaris verification requires a harness that matches a profile the
   installed Evaris documents, a supported evidence schema, an explicit
   executable and permission to run commands. Check the installed Evaris
   compatibility table rather than assuming the two versions work together.
   Evaris 0.4.0 documents two actions: `check`, with a restricted
   `invaris.dev/v1alpha2` harness and `invaris.evidence/v1alpha2` evidence, and
   `campaign`, with an `invaris.campaign/v1alpha1` file whose harnesses are
   listed in `files`. Earlier Evaris versions support `check` only. Challenges
   and mutations reach Evaris only through a campaign. Report native
   verification and Evaris assessment separately: required REJECT fails;
   required REFUSE, ERROR or UNAVAILABLE is inconclusive; ACCEPT cannot
   override failed or missing task criteria.

## Output

Report experiment and evidence paths, conditions, actual outcomes, observations,
comparability, limitations and unrun steps. If no compatible authorized agent
runner is available, provide runnable cases and mark behavioral comparison
**Not Run**; never simulate independent runs or claim an improvement.
