# Structured evidence to Markdown

Use structured case records as the factual source. For substantial reports prefer
available `panda-write`, passing the case, sanitized evidence, desired applicable
file names and exact output root. Investigation and verification remain panda-blue's work.
If unavailable, use the [case template](../assets/report-templates/CASE_SUMMARY.md)
or optional deterministic renderer; no installation is required to write a report.

Load only applicable templates:

| Mode | Templates |
| --- | --- |
| hunt | [Hunt](../assets/report-templates/THREAT_HUNT_REPORT.md), [detection](../assets/report-templates/DETECTION_COVERAGE.md) when supported |
| incident | [Incident](../assets/report-templates/INCIDENT_REPORT.md), [timeline](../assets/report-templates/INCIDENT_TIMELINE.md) |
| verify | [Verification](../assets/report-templates/VERIFICATION_REPORT.md) |
| intel | Helper-generated topic report (THREAT_INTELLIGENCE.md, CVE_ANALYSIS.md, OWASP_UPDATES.md or INCIDENT_INTELLIGENCE.md), intelligence.json, source-status.json; PROJECT_EXPOSURE.md only for local matches. State assessment time, source freshness and limitations first. |

Create only mode-relevant reports named in SKILL.md and an optional CASE_SUMMARY.md.
Keep JSON records versioned even when a conventional file is named incident.json,
detection-findings.json or verification-results.json. Manually authored timeline.json must preserve original timestamps/zones,
derived UTC only when known, source event/evidence references and uncertainty;
P0 supplies no automatic timeline normalizer/schema.

Report: question/scope/permission level → supported observations → findings with
asset, invariant, expected/observed behavior and evidence IDs → severity rationale
and confidence → actual execution/verification → impact/remediation → limitations
and smallest deciding next check. A hunt/incident report needs the observed timeline and
alternative explanations. Do not invent execution or fill missing source fields.

Use concise B2 English by default, facts separate from interpretations, exact status
labels, and redacted data. No automatic external submission, publication or sharing.
Preserve originals privately. Hashes or artifact paths can themselves identify
private material; avoid including them in public summaries without need.

The helper's conservative renderer intentionally outputs reviewed fields only,
omits free-text titles/evidence/URLs/prose and raw artifacts, and refuses no facts
merely to create an optimistic summary. It cannot sanitize arbitrary prose or
replace the analyst's full report. Use the manual template for verified sanitized
details. Markdown/control-character escaping is not secret redaction.
