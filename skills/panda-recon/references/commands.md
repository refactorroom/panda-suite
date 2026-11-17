# Agent commands and help

The [command contract](../assets/command-contract.json) is the mode/input/options
source of truth. Agent invocation, helper invocation and skill installation are
different mechanisms. `$panda-recon scan ./project` is a standalone Codex prompt,
not a shell command. Installed plugins may use `$panda-suite:panda-recon`; Claude
standalone uses `/panda-recon`, plugin `/panda-suite:panda-recon`. Use the actual
host selector. Discovery is not proof an interactive model task was executed.

Help: `help` lists seven modes, inputs, outputs and boundaries. `help MODE` gives
focused help and scan defaults/options. Unknown modes/options produce a useful
error listing supported choices; do not silently dispatch a different workflow.
Missing target: inspect an explicit current project only when the context resolves
it; otherwise request that path. Invalid/inaccessible targets remain errors, not
permission to inspect parents. Help does not create reports or perform an audit.

For scan, accept quick/deep depth, minimum display severity, markdown/json/both,
an explicit output destination, repeated relative exclude paths/globs, offline and
no-tools. Defaults: quick, Informational, both, offline. No-tools means manual/static
work without scanner execution; import of already supplied reports is still allowed.
Offline prohibits remote rules/advisory services/uploads; it does not make an
arbitrary installed tool safe. Exclusions and deferred coverage must be visible.
Keep canonical findings.json complete regardless of severity/format selection.

The equivalent structured agent request is `{mode, target, options}` with scan
options `{depth, severity, format, output, exclude, offline, noTools}`. The optional
`recon.py request MODE TARGET ...` validates this grammar/path and prints the
structured request with executed=false. It performs no workflow. Other modes
retain natural-language constraints and their existing reference workflows; their
names are not new shell subcommands. Existing offline helper commands are preserved.

`recon.py help [MODE]` gives deterministic help. `recon.py scan-report TARGET`
normalizes supplied local Security/Semgrep/Gitleaks JSON and writes report views;
it never launches those producers. See [helper details](helpers.md).
