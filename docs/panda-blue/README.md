# Panda Blue v0.4.0

Panda Blue investigates supplied security evidence defensively: threat hunting,
incident reconstruction and rechecking a fix against its invariant. It also
retrieves dated public threat intelligence (CVE, KEV, EPSS, OSV, OWASP, ATT&CK)
with a visible freshness status. It never contacts assessment targets.

Panda Blue and [Panda Red](../panda-red/README.md) were split from Panda Recon in
v0.4.0. Blue keeps the defensive modes; Red keeps scanning, surface mapping, lab
validation and bounty work. Case, asset, evidence and finding records use the
shared `panda-case.*/v1` schemas, so a case can move between them.

[Quickstart](quickstart.md) · [Command reference](command-reference.md) ·
[Installation](installation.md) · [Workflows](workflows.md) ·
[Troubleshooting](troubleshooting.md) · [Scheduled refresh](scheduling.md)

| Agent mode | Purpose | Example |
| --- | --- | --- |
| hunt | Telemetry hypotheses and benign alternatives | [Log review](examples/hunt-logs.md) |
| incident | Supported incident reconstruction | [Case analysis](examples/incident-analysis.md) |
| verify | Recheck an existing finding/invariant | [Remediation](examples/verify-finding.md) |
| intel | Dated public vulnerability intelligence and project exposure | [CVE lookup](examples/intel-cve.md) |

Standalone Codex prompt: `$panda-blue incident ./case-evidence`.
Codex plugin: `$panda-suite:panda-blue incident ./case-evidence`.
Claude Code plugin: `/panda-suite:panda-blue incident ./case-evidence`.
These are agent request examples; interactive model runs of these prompts remain
**Not Run**. Natural language works too: “Use Panda Blue to reconstruct this
incident from the supplied logs only; no target contact, containment or fixes.”

For deterministic help from a source checkout:

```sh
.venv/bin/python skills/panda-blue/scripts/blue.py help
.venv/bin/python skills/panda-blue/scripts/blue.py help intel
```

Help does not perform analysis. `intel` is the only helper action that may use
the network, and only with `--allow-network`; package queries need
`--allow-package-queries`. No scheduler or monitoring runs by default.

Containment, isolation, credential revocation, source changes and external
notifications are recommendations until authorization covers them. Write can
compose substantial reports from structured facts. Blue remains usable alone.
