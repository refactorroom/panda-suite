---
name: panda-invaris
description: Inspect, author, run, and interpret Invaris harnesses, guardrail challenges, mutations, and campaigns when project verification or check effectiveness needs evidence.
---

# Panda Invaris

Use Invaris to execute configured project checks or test whether they detect a
specific deliberate change. General test design does not require Invaris; agent
and skill evaluation belongs to Evaris when that is the requested work. This
skill works independently and does not require Panda Lead or Evaris.

## Workflow

1. Establish the requested outcome and authorization: inspect or explain only,
   author or edit a harness, or run specific checks. Locate the project and the
   selected harness, inspect its version, commands, paths, policies, and potential
   side effects before running. Commands execute with the user's permissions;
   temporary workspaces do not isolate external services. Preserve existing
   configuration and user changes. Do not run untrusted commands.
2. Check the installed CLI and its version or available usage, and consult the
   matching Invaris documentation and schema. Do not assume a newer command or
   schema is supported. If unavailable, describe the missing prerequisite and
   continue with authorized inspection; do not invent execution evidence or
   install tools without authorization. When authoring, select checks that match
   the project and user request. `init` may create an empty harness; that alone
   is not verification. Use `doctor` and migration only if supported; preview
   migration and account for backups and existing files before writing.
3. Choose the action that answers the request: `check` runs guards, `run` runs
   steps and guards, `challenge` tests detection of a specified guard violation,
   `mutate` tests whether selected tests detect a specified code change, and
   `campaign` aggregates defined experiments under a policy. Inspect the selected
   action's prerequisites and actual command syntax. Run only authorized work;
   report actual command, harness, relevant version, exit status and evidence.
4. Interpret the native report, including coverage and policy. A passing check
   or baseline does not prove that a guard detects violations. Distinguish strong
   structured proof from legacy weak marker evidence; PROVEN from UNPROVEN and
   INCONCLUSIVE; KILLED from SURVIVED, INVALID and INCONCLUSIVE. For campaigns,
   preserve mixed, incomplete, filtered and ineligible results; do not treat a
   missing score as success. Exit 2, missing tools, timeout, refusal or invalid
   evidence is not a pass. Use the relevant action's documented exit semantics.
5. If Evaris integration is requested, consult its current compatibility contract:
   integration is optional and narrower than Invaris itself. Do not imply that
   a standalone campaign is an Evaris evaluation or that Invaris ACCEPT proves
   task completion. Report verification and Evaris assessment separately.

## Output

Give the outcome, executed or proposed action, configuration and evidence paths,
actual verdicts and meaningful limitations. State unrun checks and reasons.
Never change a report or weaken a guard to manufacture a passing result.
