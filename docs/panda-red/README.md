# Panda Red v0.4.0

Panda Red maps authorized security surfaces, runs a requested repository `scan`
workflow using available Panda Security analysis, validates invariants in an
approved lab and prepares bug-bounty cases. Active work always needs an
engagement that names exact targets, techniques and budgets.

Panda Red and [Panda Blue](../panda-blue/README.md) were split from Panda Recon in
v0.4.0. Red keeps the offensive and assessment modes; Blue keeps hunting, incident
reconstruction, fix verification and threat intelligence. Case, asset, evidence and
finding records use the shared `panda-case.*/v1` schemas, so a case can move
between them.

[Quickstart](quickstart.md) · [Command reference](command-reference.md) ·
[Installation](installation.md) · [Workflows](workflows.md) ·
[Troubleshooting](troubleshooting.md)

| Agent mode | Purpose | Example |
| --- | --- | --- |
| scan | Code/configuration security concerns, with manual validation | [Source scan](examples/scan-codebase.md) |
| recon | Authorized assets, interfaces and trust boundaries | [Surface map](examples/recon-project.md) |
| simulate | Approved synthetic invariant tests | [Local lab](examples/simulate-local.md) |
| bounty | Policy-bound validation/submission preparation | [Program policy](examples/bug-bounty.md) |

Standalone Codex prompt: `$panda-red scan ./project --depth quick --no-tools`.
Codex plugin: `$panda-suite:panda-red scan ./project --depth quick --no-tools`.
Claude Code plugin: `/panda-suite:panda-red scan ./project --depth quick --no-tools`.
These are agent request examples; interactive model runs of these prompts remain
**Not Run**. Natural language works too: “Use Panda Red to scan this local
project, quick depth, static analysis only; no scanner execution, network or fixes.”

For deterministic help from a source checkout:

```sh
.venv/bin/python skills/panda-red/scripts/red.py help
.venv/bin/python skills/panda-red/scripts/red.py help scan
```

Help does not perform analysis. Default scan behavior is quick/offline; missing
scanners are skipped visibly. The optional `scan-report` helper imports local
results and validates source locations; it never executes a scanner or a model.
Panda Red makes no network lookups; for current CVE, KEV or EPSS status use Panda
Blue `intel` and pass its dated output in.

Source/configuration auditing reuses `panda-security` when available. Write can
compose substantial reports from structured facts. Red remains usable alone.
Active testing, remote scans/uploads, installations, production changes and
external submissions require authorization covering those actions. A manifest
grants no authority.
