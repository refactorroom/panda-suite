# Optional offline helper

`scripts/recon.py` requires Python 3.10+ and `jsonschema` 4.18+ with its bundled
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
.venv/bin/python skills/panda-recon/scripts/recon.py validate engagement engagement.json
.venv/bin/python skills/panda-recon/scripts/recon.py validate case case.json
.venv/bin/python skills/panda-recon/scripts/recon.py inventory engagement.json assets.json
.venv/bin/python skills/panda-recon/scripts/recon.py scope engagement.json https://app.example.test/api/items --resolutions resolutions.json --redirects redirects.json --technique http-get --at 2026-11-17T09:00:00Z
.venv/bin/python skills/panda-recon/scripts/recon.py integrity case.json --root ./private-evidence
.venv/bin/python skills/panda-recon/scripts/recon.py transition case.json --to collecting --reason "Read supplied synthetic export" --at 2026-11-17T09:01:00Z
.venv/bin/python skills/panda-recon/scripts/recon.py render case.json
```

Use the actual current authorized time for real cases. The illustrated scope
command never sends HTTP or queries DNS. resolutions.json is a supplied object
mapping exact normalized hosts to IP arrays; redirects.json is a supplied array.
Each URL hop and every supplied address must match an explicit target and avoid
exclusions. Query strings, fragments, percent encodings, userinfo, dot segments,
wildcards, ambiguous numeric hosts and non-HTTP protocols are unsupported. This
conservative subset can reject valid URLs; it never falls back to broader scope.
Time/rate/total/duration observations are caller-supplied, not a live counter.

Exit 0 means a valid record, matched supplied scope, matched integrity or successful
offline transformation, depending on action. Exit 2 means refusal, mismatch,
unavailable evidence/dependency or inconclusive scope. It never means clean security.
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

## v0.2.0 additions

`help [MODE]` and `request MODE TARGET [scan options]` use only the standard
library and execute no workflow. `scan-report TARGET` performs bounded local
inventory and normalizes explicit local `--security-report`, `--semgrep-report`
and `--gitleaks-report` inputs; it never launches producers. Existing commands
and v1 records remain valid; scan fields are additive. See the skill-local
[command contract](commands.md) and [scan workflow](scan.md).

Scan-report writes fresh private canonical JSON, metadata and requested Markdown.
Exit 0 means normalization/publication completed, 3 means input processing was
partial and 2 means error/refusal. Assessment stays Partial and toolsExecuted empty
for helper output even on exit 0. Severity affects Markdown/summary only; canonical
JSON retains all distinct findings and correlated aliases. Redaction combines
Gitleaks Secret values, optional private exact-value JSON and common patterns;
review unrecognized prose/paths manually. No raw scanner messages are copied.
