# Command reference

## Three mechanisms

| Mechanism | Real behavior |
| --- | --- |
| Agent prompt | Selected skill interprets mode, target and constraints using host tools; not a shell process. |
| Python helper | `blue.py help`, `request`, `validate`, `integrity`, `transition` and `render` execute deterministic local operations. `blue.py intel` is the only helper that may contact the network, and only with `--allow-network`. |
| Installation | `panda-suite install/update` or a host plugin command copies/loads definitions; it does not execute modes. `npx skills` is not a panda-blue executor. |

Agent syntax below is an instruction contract, not a universal positional-argument
API. Helper request validation and host discovery are verified separately; model
execution of agent prompts remains Not Run. For plugins substitute the names in
[installation](installation.md); natural language expressing the same fields works.

## Agent help and inputs

`$panda-blue help` lists modes, inputs, outputs and boundaries. `$panda-blue help
hunt` or `help incident` gives focused help. Help creates no case or scan. Unknown
mode/options return supported choices; never silently switch workflows. A bare path
with no clear question gets a bounded read-only overview or targeted clarification.

| Mode / agent cue | Required input | Optional context | Expected saved outputs | Common failure / boundary |
| --- | --- | --- | --- | --- |
| `$panda-blue hunt TARGET` | Supplied logs/exports and hypothesis | Time window, offsets, identity/asset context | THREAT_HUNT_REPORT.md, timeline.json, detection-findings.json | Missing clocks/telemetry; anomalies are not proof of malice. |
| `$panda-blue incident TARGET` | Alert/case evidence package | Provenance/hashes, affected assets/window | INCIDENT_REPORT.md, INCIDENT_TIMELINE.md, incident.json | Incomplete evidence; no automatic isolation/revocation or simulation-to-incident upgrade. |
| `$panda-blue verify TARGET` | Finding ID, baseline evidence and invariant | Identified revised environment, approved regressions | VERIFICATION_REPORT.md, verification-results.json | Missing/failed test cannot mean Fixed; preserve IDs and deciding gaps. |
| `$panda-blue intel TOPIC` | Topic: latest, update, status, owasp, `cve CVE-ID`, kev or incidents | --days (default 1 for latest/update, 7 for incidents), --ecosystem go/npm/pypi, --severity (keeps that CVSS severity and above, plus records without CVSS), component inventory | THREAT_INTELLIGENCE.md or topic report, intelligence.json, source-status.json; PROJECT_EXPOSURE.md only for local matches | Network not permitted or source down: stale/unavailable is shown, never fresh. KEV/EPSS are not proof of local compromise. |

Save only applicable reports at requested destinations. An answer-only request
creates none. Scan, recon, simulate and bounty belong to [panda-red](../panda-red/command-reference.md);
automated telemetry correlation and detection authoring remain deferred.

## Actual helper commands

Run `python3 skills/panda-blue/scripts/blue.py --help` for the implemented shell
parser. Use the existing `.venv/bin/python` when schema validation is needed.

| Subcommand | Behavior / requirements |
| --- | --- |
| help [MODE] | Four-mode guidance; unsupported topic exits 2. No dependency installation. |
| intel TOPIC [CVE-ID] [--allow-network] [--allow-package-queries] [--offline] [--project DIR / --components FILE] [--output NEW_DIR] | Dated public intelligence from the fixed source registry; private cache at `.panda-suite/blue/intelligence-cache`. Package names/versions go to OSV only with --allow-package-queries. Exit 3 when any enabled source is stale, unavailable or failed. |
| validate KIND FILE | KIND is case, asset, finding, evidence or intelligence. |
| request MODE TARGET | Parse/validate a structured agent request and existing local evidence path (or intel topic); outputs executed=false. Does not execute the requested workflow. |
| integrity CASE --root DIRECTORY | Retained bounded hash checks under authorized trusted roots; no originals changed. |
| transition CASE --to STATE --reason TEXT --at OFFSET_TIMESTAMP | Retained immutable lifecycle transform to stdout. |
| render CASE | Retained conservative enum/index/count summary. New scan cases can also be summarized. |

## Exit behavior and errors

| Helper result | Exit | Meaning |
| --- | --- | --- |
| Help, valid request, successful transform/normalization | 0 | Operation completed; never implies security or absence of findings. |
| Invalid command/options, path/scope/schema/dependency, denied output or collision | 2 | Refused/error; diagnostic gives category and corrective direction without input values. |
| Intel with any enabled source stale, unavailable or failed | 3 | Output is still written; source-status says which sources are not fresh. |
| Retained integrity negative or unavailable outcome | 2 | Ineligible/mismatch/inconclusive; never a successful security check. |

Finding severity and count never determine these exits. Trusted non-concurrent roots
are assumed; hash checks are not a sandbox or a race-proof filesystem authority boundary.
