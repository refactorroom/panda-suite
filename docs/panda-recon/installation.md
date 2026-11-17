# Installation and activation

The source checkout contains Recon v0.3.0 (Suite 1.8.0). It is not a published npm/plugin update.
Read the [Suite overview and installation guidance](../../README.md) for
license, backups, managed updates and host refresh behavior. Use one method to avoid
same-named duplicate skills. The package remains `panda-suite`; no `panda-recon`
executable or separate npm package is introduced.

## From the current checkout

These are documented installation commands; global installation was not performed.
Python copying into disposable project skill directories and host discovery were
exercised separately. Replace the project destination explicitly:

```sh
python3 scripts/install-skills.py --destination /path/to/project/.agents/skills --skill panda-recon
python3 scripts/install-skills.py --destination /path/to/project/.claude/skills --skill panda-recon
```

Codex uses its installed selector or `$panda-recon`; Claude standalone uses
`/panda-recon`. Restart/refresh after changing skill files. GitHub installation means
obtaining the desired source revision and using one of these real host/install
mechanisms, not executing a repository's skill modes through `npx skills`.

For local plugin discovery/testing without a persistent install:

```sh
claude --plugin-dir "$PWD" plugin details panda-suite
python3 tests/check_codex_discovery.py
```

An interactive Claude plugin session can load with `claude --plugin-dir "$PWD"`;
this is documented, not an interactive model run performed here. Plugin prompts
use `/panda-suite:panda-recon`; Codex plugin selectors expose
`panda-suite:panda-recon` and can be requested with `$panda-suite:panda-recon`.
The host inventory proves discovery, not that the model followed a prompt.

## npm distribution

The registry metadata and published 1.7.2 tar member layout were inspected during
this change. Its executable is `panda-suite` at `bin/panda-suite.js`, an installer
with `install` and `update`; it does not run scan/recon/incident. The current
source enhancement is not made available by installing that older publication:
the inspected archive has no panda-recon files at all.
See [actual registry inspection](../../tests/results/recon-v0.2.0/published-package.json).

Conceptual installer examples for a future version bundling the desired skill
(the inspected latest 1.7.2 cannot install Recon):

```sh
npx panda-suite@latest install --skill panda-recon
npx panda-suite@latest update
```

These are installer examples, not execution commands or a claim the current latest
publication contains this enhancement. Node 26 installer tests have a recorded
pre-existing compatibility failure; use the verified checkout copy/plugin path
until that issue and a release are addressed. Existing managed copies must be
backed up/reconciled through the documented updater; never overwrite modified skills.
No install command above was used to modify user/global configuration in this task.

The bundled Python helper is invoked explicitly with an existing configured Python,
not installed as a new shell binary. Optional validation/reporting uses jsonschema;
help/request work without it. No missing package/tool is installed automatically.
