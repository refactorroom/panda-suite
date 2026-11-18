# Optional offline helper

`scripts/blue.py` (with its shared `scripts/case_core.py`) requires Python 3.10+ and `jsonschema` 4.18+ with its bundled
dependencies. Panda Suite's existing development environment supplies them; the
core skill/manual workflows do not require Python. Missing packages produce a
refusal, never an automatic installation. Windows has not been exercised.

Run from the Suite checkout with the existing configured interpreter, replacing
case paths with authorized local files. Commands write JSON/Markdown to stdout;
capture private outputs only at an explicitly approved destination. They do not
overwrite files or create a case store. `transition` outputs an updated record,
leaving the original input unchanged. `render` outputs a conservative summary,
not the full analyst-authored report.

```sh
.venv/bin/python skills/panda-blue/scripts/blue.py validate case case.json
.venv/bin/python skills/panda-blue/scripts/blue.py integrity case.json --root ./private-evidence
.venv/bin/python skills/panda-blue/scripts/blue.py transition case.json --to collecting --reason "Read supplied synthetic export" --at 2026-11-17T09:01:00Z
.venv/bin/python skills/panda-blue/scripts/blue.py render case.json
```

Use the actual current authorized time for real cases. panda-blue has no scope,
inventory or scan-report action; those belong to panda-red.

Exit 0 means a valid record, matched integrity or successful
offline transformation, depending on action. Exit 2 means refusal, mismatch or
unavailable evidence/dependency. It never means clean security.
Commands reject duplicate JSON keys, non-finite numbers and documents over 1 MiB.
Evidence hashing is limited to 10 MiB per regular local artifact and 50 MiB total
artifact reads per invocation. Empty integrity sets are inconclusive (exit 2), not
a successful verification. Schema resources are fixed local files, with no network
resolver. Error messages omit input values.

Hash/path checks assume a trusted evidence root without concurrent hostile changes;
they are not race-proof forensic acquisition or a same-user sandbox. Hash matches
do not authenticate the source. Validation checks schema/history/references, not
truth, root-cause deduplication or authority. The conservative renderer emits only
enums, indexes and counts; free text, raw IDs, locators, hashes and artifacts stay
in the private structured record. Use the report template for reviewed sanitized
narrative and preserve originals separately.

## Requests

`help [MODE]` and `request MODE TARGET` use only the standard library and execute
no workflow. `intel` is the only action that may use the network, and only with
`--allow-network`; see [threat intelligence](threat-intelligence.md).
