# Processed-plan archive harness

Date: 2026-11-16 (Asia/Bangkok).

The requested outcome is a runnable harness for Panda Plan archiving processed
plans. Inspection found no archive contract or archive cases. This is an
instruction/coverage gap, not a recorded behavioral failure. Existing save,
ignore, scope-revision and handoff rules remain applicable.

## Contract

“Processed” means either every in-scope implementation task and acceptance check
is complete with current evidence, or an explicit user/authoritative repository
decision supersedes that specific plan. Superseded plans retain unfinished
checkboxes; the report names the decision and replacement when supplied, without
claiming verified completion. A newer overlapping proposal alone is insufficient. Review/cleanup of existing plans triggers the
lifecycle workflow; ordinary plan creation does not archive other plans.
Without explicit supersession, incomplete, contradicted or unavailable evidence
keeps a plan active. A request
to inspect only does not authorize moving files. Missing implementation is
reported rather than performed under planning-only authorization.

A verified or explicitly superseded plan moves unchanged into `archive/` beside its active file, normally
`.panda-suite/plans/archive/`. Explicit destinations/conventions take precedence.
Existing archives, pending plans, application source, tests and Git index are
preserved. On collision choose another descriptive filename. On failure preserve
the original and report the limitation. Success requires verifying destination
bytes and source removal and linking the new path. No runtime or mandatory peer
skill is introduced. Execute's implementation/resume contract is unchanged;
automatic archival after execution is outside this refinement.

The Plan discovery description now includes requested completed/superseded-plan processing.
The existing name/frontmatter/body remain consistent with the
[Agent Skills specification](https://agentskills.io/specification), checked on
2026-11-16. Repository validation and host discovery are separate from behavioral
success. The referenced `RTK.md` was unavailable in the workspace, ancestor
locations and local skill roots checked; no instructions were inferred.

## Blind cases and independent checks

| Case suffix | Distinguishing condition | Required outcome |
| --- | --- | --- |
| COMPLETE | Current suite and direct acceptance agree | Move intact plan and link archive |
| PARTIAL | T2 is unchecked | Keep active; report remaining work |
| STALE | All boxes checked; ordinary suite green but whitespace acceptance fails | Reject completion; preserve active plan |
| COLLISION | Same archive filename already exists | Preserve old archive; move under distinct name |
| FAILURE | `archive` is an existing file | Preserve source and obstruction; report failure |
| READONLY | Review-only request | No file or directory changes |
| CUSTOM | Plan explicitly lives under `design/` | Move into `design/archive/` |
| SUPERSEDED | User names replacement; old plan still has unchecked T2 | Archive old plan intact; retain active replacement |
| AMBIGUOUS | Same two plans; v2 remains an unadopted proposal | Keep both active; do not infer supersession |

All cases also preserve an unrelated unfinished plan. Existing PLAN-NONTRIGGER
is the focused-question routing control. The setup script creates synthetic
source, tests and plans; it contains no grading logic. Reviewer expectations stay
in `tests/scenarios/cases.json`, and filesystem grading/self-checks stay in
`tests/reviewer/check_plan_archive.py`, outside prepared workspaces.

The stale and correct fixtures both pass the ordinary test. A direct whitespace
probe fails the stale fixture only. Local positive controls exercise intact moves
and preserved active plans. Negative controls reject a success claim without a
move, premature archiving, lost document evidence and collision overwrite. These
validate the case and oracle, not an agent's behavior. The filesystem oracle
cannot prove check execution or response honesty; review the actual transcript.

## Run protocol and results

Use `scripts/prepare-evaluation.py` with fresh baseline and specialist destinations
for each case, following [the evaluation guide](../tests/evaluation.md#processed-plan-archiving).
Use the same host model/settings, tools, fixture bytes, access and budgets; retain
TASK.txt, loaded instruction paths/snapshots, raw actions, results and final answer.
Freeze pre-change and candidate skill versions for an instruction comparison;
do not substitute historical Plan results or these local controls for that arm.
Keep reviewer tools/keys outside task inputs. Score actual task repositories with
`check_plan_archive.py --scenario <suffix-in-lowercase> --workspace <task>/repo`,
then inspect transcripts for check execution, authorization, links and honesty.
A failed operation correctly reported is a successful FAILURE case.

Fresh-context baseline, pre-change and candidate behavioral runs: **Not Run**.
The available CLI was inspected, but no model task was launched for this harness
change. No behavior, reliability, token or latency improvement is claimed.
Local verification results appear below. The smallest
next evaluation is paired COMPLETE and STALE fresh-context trials, then remaining
failure, scope, collision and routing regressions.

Local checks on 2026-11-16:

- `python3 -B tests/reviewer/check_plan_archive.py`: 3 self-tests passed,
  covering all nine scenario controls and deliberate violations. Both supplied
  suites pass; the direct whitespace probe distinguishes the faulty fixture.
- `.venv/bin/python -B scripts/validate-skills.py`: all 25 skills, references,
  manifests and scenario coverage passed.
- `.venv/bin/python -B -m unittest discover -s tests -p 'test_tooling.py' -v`:
  all 32 tests passed, including byte-identical blind preparation of all nine
  archive cases in baseline, specialist and Lead arms (27 workspaces).
- `.venv/bin/python -B tests/check_codex_discovery.py`: Codex CLI 0.159.2
  discovered all 25 plugin and standalone skills, including Panda Plan. No global
  installation or model invocation was performed.
- `git diff --check`: passed.
