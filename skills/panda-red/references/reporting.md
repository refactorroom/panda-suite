# Structured evidence to Markdown

Use structured case records as the factual source. For substantial reports prefer
available `panda-write`, passing the case, sanitized evidence, desired applicable
file names and exact output root. Discovery and validation remain panda-red's work.
If unavailable, use the [case template](../assets/report-templates/CASE_SUMMARY.md)
or optional deterministic renderer; no installation is required to write a report.

Load only applicable templates:

| Mode | Templates |
| --- | --- |
| recon | [Surface](../assets/report-templates/ATTACK_SURFACE.md), [report](../assets/report-templates/RECON_REPORT.md) |
| simulate | [Simulation](../assets/report-templates/SIMULATION_REPORT.md), [detection](../assets/report-templates/DETECTION_COVERAGE.md) |
| bounty | [Submission draft](../assets/report-templates/BUG_BOUNTY_REPORT.md) |
| scan | SECURITY_SCAN.md, findings.json and scan-metadata.json (see [scan](scan.md)) |

Create only mode-relevant reports named in SKILL.md and an optional CASE_SUMMARY.md.
Keep JSON records versioned even when a conventional file is named
simulation-results.json.
asset-inventory.json uses an object with engagementId and an assets array of asset
records.

Report: question/scope/permission level → supported observations → findings with
asset, invariant, expected/observed behavior and evidence IDs → severity rationale
and confidence → actual execution/verification → impact/remediation → limitations
and smallest deciding next check. A bounty report also needs the inspected policy
and permitted reproduction. Do not invent execution or fill missing source fields.

Use concise B2 English by default, facts separate from interpretations, exact status
labels, and redacted data. No automatic external submission, publication or sharing.
Preserve originals privately. Hashes or artifact paths can themselves identify
private material; avoid including them in public summaries without need.

The helper's conservative renderer intentionally outputs reviewed fields only,
omits free-text titles/evidence/URLs/prose and raw artifacts, and refuses no facts
merely to create an optimistic summary. It cannot sanitize arbitrary prose or
replace the analyst's full report. Use the manual template for verified sanitized
details. Markdown/control-character escaping is not secret redaction.
