# Evidence and case records

Use the [case](../schemas/case.schema.json), [evidence](../schemas/evidence.schema.json)
and [finding](../schemas/finding.schema.json) schemas. Keep original bytes in a
private authorized evidence root, separate from sanitized reports. P0 JSON helpers
never collect from live services or modify originals. Record provenance and
collection limitations; a provided hash is not an authenticated chain of custody.

Evidence records preserve case/source IDs, collection time, original timestamp/zone
where known, artifact reference/hash, method, related findings, sensitivity,
redaction and integrity status. Unknown is explicit, not guessed. Hash checks must
read only bounded regular files under the supplied root; reject traversal, links,
special files and missing artifacts. Preserve a mismatch; do not update the
reference hash to make evidence pass. Sanitized copies get their own identity/hash.

Case lifecycle is an auditable JSON history, not a daemon or mandatory service.
Record from/to, reason and timestamp for each transition. The helper starts from
`created`, validates a continuous history and accepts these transitions:

| From | Allowed next states |
| --- | --- |
| created | scoped, blocked |
| scoped | collecting, blocked |
| collecting | analyzing, blocked |
| analyzing | validating, reviewed, blocked |
| validating | analyzing, reviewed, blocked |
| reviewed | analyzing, reported, blocked |
| reported | analyzing, closed, blocked |
| blocked | scoped, collecting, analyzing, validating |
| closed | none |

Do not mark closed from a failed tool run or missing required evidence. Keep
inconclusive conclusions and blocked work visible. The helper checks state shape,
not whether a human review truly occurred. Preserve previous records rather than
overwriting them silently. Additional evidence can require a new analysis record;
do not erase an unfavorable conclusion or invent a past transition.

Use stable finding IDs, retain imported Security IDs when mapping fields, and
deduplicate by underlying cause/asset/invariant rather than scanner row count.
Severity describes supported impact; confidence describes evidence strength.
Keep vulnerability status, verification outcome and incident classification
independent. A simulation case is Simulation only even if it proves a lab weakness.

JSON validation rejects malformed/dangling references and duplicate record IDs;
it cannot prove an observation, classify intent, redact every secret or detect every
semantic duplicate. Do not print raw evidence to diagnose a validation failure.
