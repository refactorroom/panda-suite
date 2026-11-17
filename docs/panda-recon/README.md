# Panda Recon v0.3.0

Panda Recon maps authorized security surfaces, investigates supplied evidence and
runs a requested repository `scan` workflow using available Panda Security analysis.
It preserves findings across investigation, controlled validation and verification.

v0.3.0 adds the `intel` mode: dated CVE, KEV, EPSS, OSV, OWASP, ATT&CK and
advisory lookups with a visible freshness status, plus `--intel` for scan, hunt and
incident. Network use is opt-in; see the [release notes](../v1.8.0.md).

v0.2.0 added mode help/request validation, scan-result normalization, provenance
and report bundles. It does not add a scanner engine, target probe, agent runtime,
automatic containment or autonomous exploit loop. The npm CLI remains an installer.

[Quickstart](quickstart.md) · [Command reference](command-reference.md) ·
[Installation](installation.md) · [Workflows](workflows.md) ·
[Troubleshooting](troubleshooting.md) · [Change and validation record](../panda-recon-v0.2.0.md)

| Agent mode | Purpose | Example |
| --- | --- | --- |
| scan | Code/configuration security concerns, with manual validation | [Source scan](examples/scan-codebase.md) |
| recon | Authorized assets, interfaces and trust boundaries | [Surface map](examples/recon-project.md) |
| simulate | Approved synthetic invariant tests | [Local lab](examples/simulate-local.md) |
| hunt | Telemetry hypotheses and benign alternatives | [Log review](examples/hunt-logs.md) |
| incident | Supported incident reconstruction | [Case analysis](examples/incident-analysis.md) |
| bounty | Policy-bound validation/submission preparation | [Program policy](examples/bug-bounty.md) |
| verify | Recheck an existing finding/invariant | [Remediation](examples/verify-finding.md) |
| intel | Dated public vulnerability intelligence and project exposure | [CVE lookup](examples/intel-cve.md) |

Standalone Codex prompt: `$panda-recon scan ./project --depth quick --no-tools`.
Codex plugin: `$panda-suite:panda-recon scan ./project --depth quick --no-tools`.
Claude Code plugin: `/panda-suite:panda-recon scan ./project --depth quick --no-tools`.
These are agent request examples. Inventory discovery and helper parsing are tested;
interactive Codex/Claude model runs of these prompts remain **Not Run**. Use the
installed selector or natural language: “Use Panda Recon to scan this local project,
quick depth, static analysis only; no scanner execution, network or fixes.”

For deterministic help from a source checkout:

```sh
.venv/bin/python skills/panda-recon/scripts/recon.py help
.venv/bin/python skills/panda-recon/scripts/recon.py help scan
```

Help does not perform analysis. Default scan behavior is quick/offline; missing
scanners are skipped visibly. The optional `scan-report` helper imports local
results and validates source locations; it never executes a scanner or a model.
Its canonical JSON is unfiltered, and its assessment stays Partial pending review.

Source/configuration auditing reuses `panda-security` when available. Write can
compose substantial reports from structured facts; Debugger, Plan and approved
implementation workflows are optional. Recon remains usable alone. Active testing,
remote scans/uploads, installations, production changes and external submissions
require authorization covering those actions. A manifest grants no authority.
