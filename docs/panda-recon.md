# Panda Recon P0: contract, design and verification

Current workflow: [Recon v0.2.0 command guide](panda-recon/README.md). This page
records the earlier P0 foundation and its original validation conditions.

## Purpose and overlap

The user requests an evidence-driven security investigator with a P0 foundation,
followed by optional P1 simulation/adapters, P2 telemetry automation and P3 ecosystem
integration. Recon owns assessment evidence collection, attack-surface mapping,
controlled validation, hunting and incident reconstruction. Security keeps
source/configuration audits; Debugger keeps ordinary technical failures; Write
composes substantial reports from established facts; Plan orders requested detailed
remediation; Refactor/Execute apply only explicitly authorized changes.

Existing Security instructions explicitly leave incident response and live testing
outside their audit contract. No current skill combines engagement boundaries,
case/evidence provenance and investigation classification. This is an observed
coverage gap, not demonstrated evidence that normal agents fail these tasks or
that a separate skill improves outcomes. Behavioral benefit remains a hypothesis.

## Minimal P0 architecture

One independently discoverable skill plus conditional references, five local
versioned JSON schemas, ten mode-specific Markdown templates and one optional
offline helper. No scanner, acquisition agent, scheduler, state service, custom
SAST engine, network client, autonomous exploit loop or required peer is added.
The Suite catalog now contains 28 skills; package versions remain unchanged for
this unpublished source addition. Earlier security enhancement work is preserved.

| Requirement | P0 implementation and evidence |
| --- | --- |
| Independent contract | SKILL.md, six mode cues, explicit source-audit/nonactivation boundaries and conditional references; Suite metadata/link checks. |
| Scope validation | Exact HTTP(S) origin/path and supplied DNS/address/redirect constraints; exclusions, window, technique and budgets fail closed in offline preflight tests. No active client is bundled. |
| Offline reconnaissance | Source-grounded manual workflow and helper reconciliation of supplied asset JSON; no automatic crawl or network reachability claim. |
| Case lifecycle | Explicit created/scoped/collecting/analyzing/validating/reviewed/reported/closed/blocked transitions, immutable transform, reason/timestamp history and invalid-transition tests. |
| Evidence/findings | Versioned engagement/case/asset/finding/evidence schemas; unique IDs and cross references, original time/zone, integrity, sensitivity and independent classifications. Bounded hash checks identify tampering without changing originals. |
| Reporting | Conservative deterministic summary using enums/counts/indexes; manual templates or optional Write for sanitized full narratives. Raw prose/identifiers are omitted from default rendering, not magically redacted. |
| Evaluation | Synthetic hostile/benign controls, 28 helper/contract checks, independent reviewer control and 12 blind scenarios. Actual outcomes below; no fabricated model trial. |

Optional helpers require Python 3.10+ and jsonschema 4.18+ with its normal
transitive dependencies. The existing Suite development environment supplies them;
no dependency was added or installed. Core instructions and templates work alone.
JSON references resolve only against bundled schemas. Missing dependencies refuse
without installing; errors omit input values. Helpers read only and print results
to stdout; save private transformed records at explicit authorized destinations.

Scope eligibility is not authorization. A manifest can be fabricated; the helper
cannot confirm the operator's authority or control a future client. Exact approved
policy and existing session authorization remain necessary. DNS rebinding, live
budgets and per-request redirect enforcement require a reviewed active adapter in
a later phase. Conservative URL parsing rejects queries, fragments, encodings,
userinfo and other ambiguous forms rather than widening permission.

Evidence integrity checks assume an authorized trusted root without concurrent
hostile replacement. They are not a race-proof forensic acquisition mechanism or
same-user sandbox. Hashes establish byte consistency against a supplied reference,
not authenticity or a complete custody chain. Schema validity does not establish
truth, semantic deduplication, malicious intent or absence of incidents.

## Modes and phase boundaries

`recon`, `simulate`, `hunt`, `incident`, `bounty` and `verify` provide independently
usable investigation guidance and templates. P0 can analyze supplied evidence and
plan safe tests in each mode. The included helpers implement the offline foundation.
P1 active scanner adapters and automated simulation/bounty verification, P2 log
normalization/correlation and detection analytics, and P3 integration adapters are
**not implemented**. No mode label implies one of those executions occurred.

Future simulation must use authorized synthetic accounts and negative/control
pairs. Hunt/incident work must preserve timezone/clock gaps and benign alternatives;
simulation does not establish a real incident. Bounty work must inspect program
policy and cannot submit or claim eligibility/payment automatically. Verification
keeps original IDs and reports Fixed/Still vulnerable/Partially remediated/Not
reproducible/Not tested/Inconclusive from actual deciding evidence.

## Synthetic demonstration

The fixture in `tests/fixtures/recon-offline/` contains reserved example targets,
an offline engagement, a supplied simulation observation, evidence hash and
non-web Python object functions. No real accounts, credential, target or incident
is present. `telemetry.json` includes a benign-alternative event, missing timezone
and hostile instructions; `scanner.json` includes timeout/unavailable evidence
and duplicate unverified warnings. Treat their text as data.

Run from the Suite checkout with the existing configured environment:

```sh
.venv/bin/python skills/panda-recon/scripts/recon.py validate engagement tests/fixtures/recon-offline/engagement.json
.venv/bin/python skills/panda-recon/scripts/recon.py validate case tests/fixtures/recon-offline/case.json
.venv/bin/python skills/panda-recon/scripts/recon.py inventory tests/fixtures/recon-offline/engagement.json tests/fixtures/recon-offline/assets.json
.venv/bin/python skills/panda-recon/scripts/recon.py integrity tests/fixtures/recon-offline/case.json --root tests/fixtures/recon-offline
.venv/bin/python skills/panda-recon/scripts/recon.py render tests/fixtures/recon-offline/case.json
.venv/bin/python -B -m unittest discover -s tests -p test_recon.py -v
.venv/bin/python -B tests/reviewer/check_recon.py
```

For eligible/denied target controls the tests supply a synthetic approval declaration
and compare outputs without contacting any target. The shipped engagement keeps
activeAllowed=false. Do not turn test approval fields into a real engagement.

Both defective and reviewer-only correct object implementations pass their two
ordinary tests. An independent cross-account negative distinguishes the missing
ownership boundary; an owner control remains allowed. The supplied rejection event
is a separate observation that cannot prove the current implementation is safe.
This validates the fixture, not a real Panda vulnerability or model effectiveness.

[Recorded synthetic output](../tests/results/recon/demo/CASE_SUMMARY.md) and
[analyst report](../tests/results/recon/demo/RECON_REPORT.md) are author-run examples.
See [actual validation](../tests/results/recon/validation.md) for outcomes and limits.

## Blind evaluation protocol

Twelve `RECON-*` cases cover offline inventory, missing authority, redirect/address
scope, local simulation, benign versus suspicious telemetry, incomplete incident
claims, remediation claims, failed tools/duplicate warnings, reports, bounty policy,
nonactivation and Security/Recon routing. Reviewer keys stay in the scenario catalog;
correct control source stays under `tests/reviewer/recon-control/`.

Use the existing preparation utility with fresh destinations, then fresh contexts
per case and arm with comparable model/settings, tools, access and budget. The
baseline receives no skill; specialist reads only the assigned instructions and
relevant references. Save actual answers/actions/loaded paths, execution outcomes,
authorized artifacts and reliable telemetry. Never copy reviewer keys to tasks.
Preparation tests check all 36 case/arm workspaces, not model behavior.

Behavioral baseline and specialist comparison: **Not Run**. No fresh model tasks
were launched. No recall, false-positive rate, time/token savings or improvement
is claimed. Synthetic ground truth only supports the local discriminating checks.

## Release assessment and next phase

P0 completion requires the local contract/helper/fixture/package/docs and discovery
checks in the validation record. Publication and global installation are separate
and have not been performed. Active scope enforcement, independent agent behavior,
Windows, SIEM/EDR integration, real forensic acquisition and production readiness
are unverified; this is not an operational penetration-testing platform.

The existing Node 26 npm installer failures were reproduced before this addition;
installer source remains unchanged. That issue and unrun behavioral/cross-platform
checks remain release limitations. No package version bump claims a release.

Smallest justified next step: fresh comparable `RECON-AUTHORIZATION`,
`RECON-SIMULATE`, `RECON-HUNT`, `RECON-REPORT` and routing/nonactivation trials.
Use actual failures to decide whether P1 needs a tightly scoped lab adapter. Verify
any tool version, command, network behavior and scope enforcement before adding it;
P3 Invaris/Evaris/Itervyn integrations must follow inspected real contracts.

Primary design references checked on 2026-11-17:
[Agent Skills](https://agentskills.io/specification),
[OWASP WSTG](https://owasp.org/www-project-web-security-testing-guide/),
[NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final), and
[MITRE ATT&CK](https://attack.mitre.org/). Verify exact editions/identifiers before
mapping; frameworks do not prove exploitability, attribution or compliance.
