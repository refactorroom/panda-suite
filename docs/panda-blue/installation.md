# Installation and activation

The source checkout contains Panda Blue v0.4.0. It is not a published
npm/plugin update yet. Read the [Suite overview and installation guidance](../../README.md)
for license, backups, managed updates and host refresh behavior. Use one method to
avoid same-named duplicate skills. The package remains `panda-suite`; no
`panda-blue` executable or separate npm package is introduced.

## From the current checkout

```sh
python3 scripts/install-skills.py --destination /path/to/project/.agents/skills --skill panda-blue
python3 scripts/install-skills.py --destination /path/to/project/.claude/skills --skill panda-blue
```

Codex uses its installed selector or `$panda-blue`; Claude standalone uses `/panda-blue`.
Plugin prompts use `/panda-suite:panda-blue` (Claude) or `$panda-suite:panda-blue` (Codex).
Restart/refresh after changing skill files. The skill works with only itself
installed; Panda Red and Panda Security are optional peers.

If an older copy of `panda-recon` is installed, remove it after installing this
skill; the managed updater keeps skills that the package no longer ships.

## npm distribution

The executable is `panda-suite` at `bin/panda-suite.js`, an installer with
`install` and `update`; it does not run agent modes. Once a release that contains
this skill is published:

```sh
npx panda-suite@latest install --skill panda-blue
npx panda-suite@latest update
```

The bundled Python helper is invoked explicitly with an existing configured Python,
not installed as a new shell binary. Optional validation/reporting uses jsonschema;
help/request work without it. No missing package/tool is installed automatically.
