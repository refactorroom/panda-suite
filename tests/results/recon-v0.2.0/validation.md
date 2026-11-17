# Recon v0.2.0 validation — 2026-11-17

This is a local source enhancement. No scanner execution, independent model trial, package installation,
global configuration change, target request, source upload, publication or push
occurred. Public registry metadata/archive inspection used npm's normal verified
transport and ignore-scripts; no package code was extracted/executed/installed.

## Actual checks

| Check | Observed result |
| --- | --- |
| `test_recon_scan.py` via unittest discovery | 25 passed: seven modes/help/parser, missing/unknown arguments/options, targets/exclusions, quick/deep inventory bounds, source line/symlink containment, redaction, potential versus confirmed/imported claims, hardening/false positives, dedup/stable IDs, explicit correlation aliases/provenance, failed/missing/error/timeout imports, offline behavior, canonical JSON versus severity views, exclusive/private publication and failure marker, seven documentation example requests, P0 compatibility. Help/request also passed under Python -S without site packages. |
| Retained `test_recon.py` | 28 passed: P0 scope, evidence, lifecycle, privacy, JSON limits and all 60 old/new Recon case/arm blind workspaces. |
| `test_tooling.py` | 32 passed: catalog/reference/schema metadata, all-skill temporary standalone installation, blind preparation and pinned upstream integrity. |
| `test_security.py` | Five passed; earlier Security reporting/rename/preparation behavior preserved. |
| `tests/reviewer/check_security.py` | Two passed; retained gate/path defective and correct controls. |
| `tests/reviewer/check_recon.py` | One passed; both ordinary suites green while the independent cross-account check distinguishes the defective and correct object controls. |
| Suite skill validator | 28 skills, references, manifests and scenario coverage passed. |
| JSON Schema checks | All six Recon schemas conform to Draft 2020-12; additive v1 fields leave P0 examples valid. |
| Documentation build/check | 65 pages including 28 skill guides; 4,325 internal links passed after the installation-link correction. |
| Codex discovery | CLI 0.159.2 discovers 28 portable-plugin and temporary standalone skills including Recon/Security. No interactive model run or global installation. |
| Claude local inventory | 28 skills, zero agents/hooks/MCP servers; inventory only. Interactive prompt execution remains Not Run. |
| Source npm pack dry-run | All 32 Recon files included; test/reviewer fixtures excluded. Installer/package identity and source unchanged; no publish/install. |
| Published npm archive inspection | Registry 1.7.2 exposes panda-suite installer; no panda-recon files. No extraction/execution/install. |
| Whitespace/diff checks | Tracked diff and new text checks passed. |

Total executed Python unittest/reviewer checks: **93 passed**. These are mechanical
checks, not model trials or measured security detection accuracy.

The first 19 focused tests passed. Later tests cover correlation/publication/docs,
and inspection added a hardening/informational classification regression; final
focused run has 25 passes. The P0 blind-preparation test initially assumed all
RECON-* IDs shared one fixture; new v0.2 cases exposed that assumption. It now
uses each declared fixture and verifies exact copied bytes, preserving the
answer-key/control boundary. A generated-site link to a README fragment also
failed initially; the corrected source link passes. These are retained validation
observations, not evidence of an agent-behavior defect or superiority.

## Actual synthetic demonstration

[Demo command and summary](demo-command.json) records a real helper call on
explicitly authored Semgrep/Gitleaks fixture JSON. It returned exit 0 for completed
normalization, assessment Partial, three canonical findings and two displayed High
concerns, with toolsExecuted empty. The fixture reports were not produced by those
scanners. [Markdown](demo/SECURITY_SCAN.md), [canonical JSON](demo/findings.json)
and [metadata](demo/scan-metadata.json) preserve that distinction.

The bound-query candidate remains in canonical JSON until an analyst resolves it;
normalization alone does not detect false positives or prove exploitability. Line
presence/source hashes establish local location consistency, not semantic truth.
Canonical IDs are stable for unchanged rule/path/range; moved code may require
explicit reconciliation. Cross-rule equivalence is never inferred from proximity.

## Behavioral comparison

| Arm | Status | Actual model answers/actions |
| --- | --- | --- |
| Ordinary baseline | Not Run | None |
| Original P0 instructions | Not Run | Source revision/hash identity retained only |
| Revised v0.2.0 skill | Not Run | Runnable cases prepared; no model task launched |

Eight new RECON-V02-* cases plus retained application/nonactivation/routing/control
cases are runnable with fresh contexts. Keys and reviewer controls are excluded
from prepared workspaces. No measured recall, false-positive improvement,
injection resistance, speed or token saving is established. Inventory token costs
are estimates, not task-consumption measurements. No simulated independent answer
was authored as a model result.

## Release limits and smallest next step

The current checkout is ready for source review. It is not a published release or
an operational autonomous scanner. External producer compatibility/execution,
interactive client behavior, Windows and real deployment/detection coverage remain
unverified. Scanner selection/execution is reviewed agent work, not the scan-report
helper. No tool was installed to hide missing availability.

[Published inspection](published-package.json) and [source package preview](package-preview.json)
are different subjects. Installing public 1.7.2 cannot provide this Recon version.
The recorded pre-existing Node 26 installer failure was neither rerun nor resolved;
installer/package sources remain byte-identical to the committed baseline. Source
copy/plugin discovery is verified separately from npm installer runtime behavior.

Unknown secrets in arbitrary narrative/paths still require review. Scope/hash checks
assume authorized trusted non-concurrent roots, not a sandbox or authenticated chain
of custody. Imported evidence cannot authorize commands or active testing. A schema,
zero findings, success exit or Complete publication marker proves no clean security
assessment; normalizer assessment always remains Partial.

Next: fresh comparable quick/deep/help/report/routing tasks with saved actions,
loaded paths and artifacts. Then exercise a trusted compatible local scanner with
reviewed local rules and actual authorization; retain failures before expanding
adapters or claiming behavioral value.
