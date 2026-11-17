# Panda Security: enhancement, migration and evaluation

## Decision and evidence

Enhance and rename `panda-sec` to `panda-security`, as requested, keeping one
security skill and twenty-seven Suite skills. Application analysis, dependency
applicability, secret handling and evidence-ranked findings already existed.
Dedicated agent/MCP/harness guidance, named modes and a machine-readable reporting
contract were missing from the inspected instructions. These are instruction
gaps, not demonstrated model failures or proof the revision improves behavior.

The [original instructions](../tests/results/security-rebrand/original/panda-sec/SKILL.md)
and their reference are frozen for comparison. Historical answers, loaded paths
and hashes retain `panda-sec`; the v1.1.0 note links to that snapshot.

The design follows [Agent Skills](https://agentskills.io/specification) metadata.
[OWASP AI Agent Security](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html)
and [ASVS](https://asvs.owasp.org/) inform applicable review prompts, without
establishing compliance or exhaustive coverage.

## Contract and implementation

Trigger on a dedicated audit or remediation verification of application,
dependency, CI/CD, skill, MCP or harness security. A focused explanation, general
changed-code review, skill-effectiveness evaluation or request merely to run
verification is a non-trigger. Lead routing distinguishes those tasks.

| Mode | Contract |
| --- | --- |
| quick | Bounded high-risk triage; deferred coverage stays visible. |
| deep | Applicable cross-boundary analysis across explicit scope. |
| skills | Instructions, references, scripts, hooks, tools/MCP and harnesses. |
| verify | Preserve finding IDs; recheck current guards and regression evidence. |

Keep the original application reference; add conditional agent, harness,
supply-chain, scanner and reporting references. No SAST engine, scanner adapter,
runtime, install hook or new dependency is added. Permission rules are instructions,
not programmatic read-only enforcement or a sandbox. External tools are optional.

Outputs contain scope/revision, threat model, evidence-ranked findings, impact,
controls considered, remediation, regressions, actual checks and limitations.
Markdown is the ordinary answer; requested files follow the
[usage examples](usage.md#panda-security). JSON uses `panda-security.findings/v1`.
Shape validation cannot establish truth, secret removal or root-cause deduplication.
Audit authority does not authorize repairs, installations, uploads or global changes;
existing explicit scoped repair authorization remains valid.

## Local harness evidence

The authoring review inspected adjacent Invaris, Evaris and Itervyn projects.
[Source identities](../tests/results/security-rebrand/source-review.json) record
revisions and relevant hashes. Inspected source is not runtime compatibility proof.

| Project | Boundary carried into conditional guidance |
| --- | --- |
| Invaris | Trusted commands are not sandboxed; network declarations and writable replacement paths have narrower effects. Input/evidence versions, required gates, weak markers, challenge/mutation/campaign coverage and cleanup differ. |
| Evaris | Prepare/import does not launch agents. Command graders/verifiers need opt-in; scratch snapshots, exclusions and linked dependencies do not contain external effects. Private oracles, evidence identity, required criteria and its restricted Invaris profile matter. |
| Itervyn | Exact provider versions/profiles matter. Process failures survive PASS payloads; required aggregation and complete publication matter. Live projects and imported runs are different subjects. Advisory next actions do not authorize repairs. |

Installed Evaris reported `v0.2.0`; reviewed source describes 0.4.0. Installed
Invaris returned exit 2, `unsupported action: --version`; its version remains
unknown. Itervyn was not found on PATH. No harness, provider or command grader
was launched. Reinspect matching contracts when auditing another build.

## Evaluation and limits

Eleven new `SECURITY-*` cases supplement six retained `SEC-*` cases. They cover
harness gate/path violations, injection versus benign examples, MCP hints versus
authorization, failed/offline/malformed scan evidence, stale fix claims, saved
reports, privileged CI, false sandbox assumptions, missing non-web context,
scope pressure and nonactivation. Keys remain in `tests/scenarios/cases.json`.

Prepare separate fresh workspaces with unused destinations:

```sh
python3 scripts/prepare-evaluation.py --case SECURITY-HARNESS --arm baseline --destination /tmp/panda-security-harness-baseline
python3 scripts/prepare-evaluation.py --case SECURITY-HARNESS --arm specialist --destination /tmp/panda-security-harness-candidate
```

For an original-skill arm, prepare another baseline copy and supply the frozen
original instructions separately. Never copy reviewer keys or the correct control.
Freeze candidate instructions for recorded trials. Use fresh contexts per case/arm
and comparable model/settings, budget, tools and access. Save answers, actual actions,
loaded paths, checks, artifact hashes and unknown metadata. Score correctness,
evidence, completion, authorization, honesty and usefulness independently. Measure
overhead only from exposed telemetry; file size does not establish token savings.

The fixture's three ordinary tests pass on defective and correct implementations.
Independent probes distinguish timeout/exit bypass and traversal/absolute/symlink
escapes. The correct control stays under `tests/reviewer/security-control/`, outside
the fixture. `python3 -B tests/reviewer/check_security.py` validates that distinction,
not model resistance or a vulnerability in real Panda projects. It uses harmless
functions and temporary paths; no provider, network or exfiltration executes.

Baseline, original-skill and candidate behavioral comparisons: **Not Run**.
No fresh model tasks were launched for this authoring change. Evaris is not an
agent runner; installed tools are not assumed compatible with newer source.
No measured audit-quality, resistance, time or token improvement is claimed.
See the [actual validation record](../tests/results/security-rebrand/validation.md).

## Migration and release boundary

This is an unpublished source change. Package/plugin versions remain unchanged;
there is no second discoverable alias or automatic global migration.

- Standalone: `$panda-security`; Codex plugin: `$panda-suite:panda-security`;
  Claude plugin: `/panda-suite:panda-security`.
- Update prompts, scripts and selectors using `panda-sec`.
- Standalone copies keep their old directory. The npm managed updater cannot
  silently rename a removed skill and preserves skills absent upstream. Preserve
  backups, explicitly install the new
  skill, then retire the old copy through the installation's documented process.
  Do not hand-edit managed state or delete modified copies automatically.
- Plugin users need an updated/published snapshot and host refresh. This checkout
  does not change installed cached plugins.

The smallest next improvement is fresh comparable trials of `SEC-MIXED`,
`SECURITY-HARNESS`, `SECURITY-AGENT`, `SECURITY-REPORT` and nonactivation controls.
Retain failures and baseline successes. Add helpers/adapters only if those trials
demonstrate a recurring mechanical gap.
