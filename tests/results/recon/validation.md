# Recon P0 validation — 2026-11-17

P0 was implemented locally in Panda Suite, preserving the earlier Security
rebrand. No target contact, active scanner, tool installation, global configuration,
publication or external evidence sharing was performed. Synthetic Python fixture
probes are local in-memory controls, not a live penetration test or real incident.

## Actual checks

| Command/check | Observed result |
| --- | --- |
| `.venv/bin/python -B -m unittest discover -s tests -p test_recon.py -v` | 28 passed: five schema examples; default deny; authorization declarations; exact origin/port/path; ambiguous URLs; all supplied addresses/redirects; windows/techniques/budgets; offline inventory; histories; IDs/references; simulation classification; tamper/missing/link/special/oversized evidence; report omission of sensitive free text; malformed/oversized JSON; missing optional dependency; no echo/read-only CLI; 36 blind case/arm workspaces. |
| `.venv/bin/python -B tests/reviewer/check_recon.py` | One passed: both two-test ordinary suites green; cross-account negative rejects the defective implementation and accepts the reviewer control's owner boundary. |
| `.venv/bin/python -B -m unittest discover -s tests -p test_tooling.py -v` | 32 passed including metadata/reference mutations, all-skill standalone installation, blind preparation and upstream integrity. |
| `.venv/bin/python -B -m unittest discover -s tests -p test_security.py -v` | Five passed; earlier Security reporting, rename and blind preparation preserved. |
| `.venv/bin/python -B tests/reviewer/check_security.py` | Two passed; earlier gate/path negative and correct controls preserved. |
| `.venv/bin/python scripts/validate-skills.py` | 28 skills, metadata, local references, manifests and scenario catalog validated. |
| `.venv/bin/python scripts/build-docs.py` | 53 pages including 28 skill guides built. |
| `.venv/bin/python scripts/check-docs.py` | 53 pages and 3,520 internal links passed. |
| `python3 tests/check_codex_discovery.py` | Codex CLI 0.159.2 discovered 28 local plugin and temporary standalone skills, including panda-recon and panda-security. Existing installed flag is app state, not an installation performed by this check. |
| `claude --plugin-dir /absolute/path/to/panda-suite plugin details panda-suite` | 28 skills; zero agents/hooks/MCP servers. Inventory only, no interactive model invocation. |
| `npm pack --dry-run --ignore-scripts --json` | Manifest parsed and checked: all 25 Recon files included; tests/reviewer fixtures excluded. No tarball installation or publication. |
| `git diff --check` and new-text whitespace inspection | Passed; original Security snapshot preserved. |

Total Python checks executed across the listed suites: 68 passed. These are
mechanical/package/control tests, not 68 model trials or evidence of field accuracy.
An initial 25-test focused run passed; review added three discriminating tests for
malformed resolution types, empty integrity sets and oversized artifacts. A numeric
JSON overflow case was added to the existing malformed-input test. Outcomes from
initial runs were not used as proof of complete contract coverage.

[Seven actual offline demo commands](demo-commands.json) preserve exits and artifact
paths. Record/case validation, inventory, integrity, conservative rendering and
immutable transition returned 0; the inactive engagement scope check returned the
expected refusal exit 2. [Package preview](package-preview.json) records included
Recon files. The examples contain synthetic data only and do not establish
operator authority, target reachability or a real security incident.

## Baseline and skill comparison

| Arm | Status | Actual model outputs/actions |
| --- | --- | --- |
| Ordinary baseline | Not Run | None |
| panda-recon specialist | Not Run | None |
| Lead routing/nonactivation | Not Run | None |

Twelve runnable RECON-* scenarios and reviewer expectations exist, with the
correct object-service control and keys kept out of prepared workspaces. Preparation
alone does not constitute a model run. No fresh model tasks were launched; no audit
accuracy, recall, false-positive rate, resistance, elapsed-time or token-saving
claim is supported. Claude inventory token figures are estimates, not actual task
consumption. Synthetic fixture discrimination does not establish behavioral benefit.

## Known limits and release assessment

Local offline P0 authoring checks pass. This source is ready for review; production
assessment readiness is not established. Active requests/scanners, live DNS/redirect
binding and budgets, automated telemetry/forensic collection, P3 adapters, Windows,
independent model behavior and operational detection coverage remain untested or
unimplemented. Report shape/history validity cannot prove authority, facts,
authenticity, intent or semantic deduplication. Hash/path checks assume a trusted
root without concurrent hostile replacement. Full analyst narratives need explicit
sanitization and review; the deterministic summary is deliberately conservative.

Existing Node 26 npm installer tests had five failures before this addition,
reproduced on pristine HEAD in the
[earlier record](../security-rebrand/npm-head-check.json). Installer code and tests
remain unchanged; that suite was not repeated here without a new installer change.
The package dry-run does not resolve its runtime compatibility limitation.

Next justified work: comparable fresh authorization, simulation, hunt, report and
routing trials. Retain failures and baseline successes before adding a narrowly
scoped P1 adapter or claiming value over ordinary agent behavior.
