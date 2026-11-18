# Agent commands and help

The [command contract](../assets/command-contract.json) is the mode/input/options
source of truth. Agent invocation, helper invocation and skill installation are
different mechanisms. `$panda-blue incident ./case` is a standalone Codex prompt,
not a shell command. Installed plugins may use `$panda-suite:panda-blue`; Claude
standalone uses `/panda-blue`, plugin `/panda-suite:panda-blue`. Use the actual
host selector. Discovery is not proof an interactive model task was executed.

Help: `help` lists four modes (hunt, incident, verify, intel), inputs, outputs and
boundaries. `help MODE` gives focused help. Unknown modes/options produce a useful
error listing supported choices; do not silently dispatch a different workflow.
Missing target: inspect an explicit current project only when the context resolves
it; otherwise request that path. Invalid/inaccessible targets remain errors, not
permission to inspect parents. Help does not create reports or perform an audit.

`intel TOPIC` takes a topic instead of a filesystem target: latest, update, status,
owasp, cve CVE-ID, kev or incidents, with optional `--days` (1–120), `--ecosystem`
and `--severity`. hunt and incident accept `--intel off|cache|live` (default
off); explicit `--offline` with `--intel live` is refused, not silently downgraded.
See [threat intelligence](threat-intelligence.md).

Requests for scan, recon, simulate or bounty are refused with a pointer to
panda-red; they are not silently dispatched.

The optional `blue.py request MODE TARGET ...` validates the grammar/path and
prints the structured request with executed=false. It performs no workflow.
`blue.py help [MODE]` gives deterministic help. See [helper details](helpers.md).
