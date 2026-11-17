# Command reference

## Three mechanisms

| Mechanism | Real behavior |
| --- | --- |
| Agent prompt | Selected skill interprets mode, target and constraints using host tools; not a shell process. |
| Python helper | `recon.py help`, `request`, `scan-report` and the seven retained offline commands execute deterministic local operations. `recon.py intel` is the only helper that may contact the network, and only with `--allow-network`. |
| Installation | `panda-suite install/update` or a host plugin command copies/loads definitions; it does not execute modes. `npx skills` is not a Recon executor. |

Agent syntax below is an instruction contract, not a universal positional-argument
API. Helper request validation and host discovery are verified separately; model
execution of agent prompts remains Not Run. For plugins substitute the names in
[installation](installation.md); natural language expressing the same fields works.

## Agent help and inputs

`$panda-recon help` lists modes, inputs, outputs and boundaries. `$panda-recon help
scan` or `help incident` gives focused help. Help creates no case or scan. Unknown
mode/options return supported choices; never silently switch workflows. A bare path
with no clear question gets a bounded read-only overview or targeted clarification.

| Mode / agent cue | Required input | Optional context | Expected saved outputs | Common failure / boundary |
| --- | --- | --- | --- | --- |
| `$panda-recon scan TARGET` | Local repository directory | Depth, filters, format, exclusions, tools restrictions | SECURITY_SCAN.md, canonical findings.json, scan-metadata.json | Invalid path, missing/erroring tools, unsupported report; local static analysis only unless separately authorized. |
| `$panda-recon recon TARGET` | Repository, asset inventory or supplied evidence | Exact scope, observation dates | ATTACK_SURFACE.md, asset-inventory.json, RECON_REPORT.md | Unknown reachability/ownership; no DNS/HTTP from passive collection. |
| `$panda-recon simulate TARGET` | Approved lab/fixtures and invariant | Synthetic accounts, negative/control pair, telemetry | SIMULATION_REPORT.md, simulation-results.json; detection report when supported | Missing authorization/environment; no uncontrolled exploit or third-party data. |
| `$panda-recon hunt TARGET` | Supplied logs/exports and hypothesis | Time window, offsets, identity/asset context | THREAT_HUNT_REPORT.md, timeline.json, detection-findings.json | Missing clocks/telemetry; anomalies are not proof of malice. |
| `$panda-recon incident TARGET` | Alert/case evidence package | Provenance/hashes, affected assets/window | INCIDENT_REPORT.md, INCIDENT_TIMELINE.md, incident.json | Incomplete evidence; no automatic isolation/revocation or simulation-to-incident upgrade. |
| `$panda-recon bounty TARGET` | Program policy and engagement | Explicit targets, permitted techniques and disclosure rules | BUG_BOUNTY_REPORT.md | Unclear policy/authority means offline draft; no submission or payout claim. |
| `$panda-recon verify TARGET` | Finding ID, baseline evidence and invariant | Identified revised environment, approved regressions | VERIFICATION_REPORT.md, verification-results.json | Missing/failed test cannot mean Fixed; preserve IDs and deciding gaps. |
| `$panda-recon intel TOPIC` | Topic: latest, update, status, owasp, `cve CVE-ID`, kev or incidents | --days, --ecosystem go/npm/pypi, --severity, component inventory | THREAT_INTELLIGENCE.md or topic report, intelligence.json, source-status.json; PROJECT_EXPOSURE.md only for local matches | Network not permitted or source down: stale/unavailable is shown, never fresh. KEV/EPSS are not proof of local compromise. |

Save only applicable reports at requested destinations. An answer-only request
creates none. The six P0 investigation workflows are preserved; automated active
simulation/telemetry/integration adapters remain deferred.

## Scan options

| Option | Values / default | Meaning |
| --- | --- | --- |
| --depth | quick / deep; quick | Agent analysis prioritization; helper inventory budgets differ, not a new SAST engine. |
| --severity | informational, low, medium, high, critical; informational | Minimum Markdown/summary display severity; canonical JSON remains complete. Case-insensitive. |
| --format | markdown, json, both; both | Views; canonical findings.json and metadata are always retained. JSON-only omits Markdown. |
| --output | New directory | Explicit report root. Default is a fresh private `.panda-suite/recon/reports/scans/<scan-id>/`. |
| --exclude | Repeat relative path/glob | Explicit exclusions; traversal/absolute patterns refused. .git is excluded by default; vendor/generated sources are not silently dropped. |
| --offline | Default enabled | No remote scanner operations/rules/advisories/uploads. Cannot make arbitrary tools safe. |
| --intel | off, cache, live; off | Also for hunt/incident. Cache reads dated snapshots offline; live needs network permission. Explicit --offline with live is refused. See [threat intelligence](../../skills/panda-recon/references/threat-intelligence.md). |
| --no-tools | Default false | Manual/static agent work; helper report imports remain allowed. No automatic tool launch even when false. |

## Actual helper commands

Run `python3 skills/panda-recon/scripts/recon.py --help` for the implemented shell
parser. Use the existing `.venv/bin/python` when schema validation is needed.

| Subcommand | Behavior / requirements |
| --- | --- |
| help [MODE] | Seven-mode guidance; unsupported topic exits 2. No dependency installation. |
| request MODE TARGET [scan options] | Parse/validate a structured agent request and existing local target; outputs executed=false. Does not execute the requested workflow. |
| scan-report TARGET [scan options] | Bounded local discovery, supplied-result normalization and private report publication. Does not discover vulnerabilities itself or run producers. |
| intel TOPIC [CVE-ID] [--allow-network] [--allow-package-queries] [--offline] [--project DIR / --components FILE] [--output NEW_DIR] | Dated public intelligence from the fixed source registry; private cache at `.panda-suite/recon/intelligence-cache`. Package names/versions go to OSV only with --allow-package-queries. Exit 3 when any enabled source is stale, unavailable or failed. |
| validate KIND FILE | Retained v1 validation; KIND now also supports scan-metadata and intelligence. |
| inventory ENGAGEMENT ASSETS | Retained supplied inventory reconciliation; no collection/crawling. |
| scope ENGAGEMENT URL --resolutions FILE --technique NAME | Retained offline eligibility check; optional supplied redirects/window/budget observations. Never authority or a target request. |
| integrity CASE --root DIRECTORY | Retained bounded hash checks under authorized trusted roots; no originals changed. |
| transition CASE --to STATE --reason TEXT --at OFFSET_TIMESTAMP | Retained immutable lifecycle transform to stdout. |
| render CASE | Retained conservative enum/index/count summary. New scan cases can also be summarized. |

Scan-report accepts repeated `--security-report FILE`, `--semgrep-report FILE` and
`--gitleaks-report FILE`. Inputs are supplied local JSON, not producer commands.
It validates source containment/exclusions and actual line ranges, preserves supplied
Security IDs/assessments as imported claims, and treats scanner matches as Potential
concern/Unknown confidence. Unknown mappings, producer errors, stale paths/ranges,
links and malformed records are refused visibly. It does not invoke a model.

`--redactions FILE` supplies a private JSON array of exact sensitive values (minimum
four characters); do not put secrets on command lines. Gitleaks Secret fields are
used for masking then omitted; raw messages/snippets are not copied. Common token,
assignment and private-key patterns are also masked. Review unknown narrative/paths.

`--correlations FILE` accepts reviewed groups like
`[{"primaryId":"SEC-id","duplicates":["F-id"],"reason":"Reviewed same root cause"}]`.
The primary assessment stays unchanged, aliases/provenance/evidence and original
producer severity/confidence/status notes survive. Cross-rule semantic equivalence
is not inferred from nearby lines. Input cycles, missing IDs and partial merges
are refused. Canonical JSON preserves all distinct findings and correlated aliases.

## Exit behavior and errors

| Helper result | Exit | Meaning |
| --- | --- | --- |
| Help, valid request, successful transform/normalization | 0 | Operation completed; never implies security or absence of findings. |
| Invalid command/options, path/scope/schema/dependency, denied output or collision | 2 | Refused/error; diagnostic gives category and corrective direction without input values. |
| Scan-report with refused input(s), including producer error reports | 3 | Bundle records Partial processing; other valid inputs survive. Assessment remains Partial. |
| Intel with any enabled source stale, unavailable or failed | 3 | Output is still written; source-status says which sources are not fresh. |
| Retained scope/integrity negative or unavailable outcome | 2 | Ineligible/mismatch/inconclusive; never a successful security check. |

Finding severity and count never determine these normalizer exits. Agent scan
statuses include completed in stated scope, findings detected, partial, missing
tool, invalid path, unsupported input, permission denied, scope violation, timeout
and scanner failure. Actual scanners have their own installed-version exit semantics;
record them separately. Helper metadata cannot claim scanner execution.

Discovery is capped at 128 files/5,000 entries/8 MiB for quick and
2,048 files/20,000 entries/32 MiB for deep; each file/report is at most 1 MiB.
At most 16 reports and 1,000 rows per report are accepted. Caps/skips are visible.
Source hashes and line presence prove location consistency, not exploitability.
Trusted non-concurrent roots are assumed; these checks are not a sandbox or a
race-proof filesystem authority boundary. Private output uses exclusive creation;
metadata publishes last, and missing metadata means incomplete publication.
