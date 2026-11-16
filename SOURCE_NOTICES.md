# Source provenance and terms

`upstream-lock.json` is the complete mapping of original files, revisions, and
SHA-256 hashes. These files are exact snapshots, not Suite-authored replacements.

## Panda Debugger

Source: https://github.com/akkaraponph/panda-debugger

Revision: `0b9f367954d59c44ee5e033859e29af0347f9267`.

The pristine upstream skill file: `vendor/panda-debugger/SKILL.md`. Active
Suite instructions and references: `skills/panda-debugger/`. Remaining tracked
files, including README, manifests, fixtures, and evaluation instructions:
`skills/panda-debugger/`.

The inspected revision contains no LICENSE file. The copyright owner confirmed
on 2026-11-16 that they own the rights and authorized redistribution of Panda
Debugger as part of the public Panda Suite npm package. This authorization does
not assign a license for other uses or further redistribution. The Suite MIT
license excludes these files.

## Buddhist Method

Panda Suite's pinned source is the
[akkaraponph/buddhist-method fork](https://github.com/akkaraponph/buddhist-method).
The original project is [nai0om/buddhist-method](https://github.com/nai0om/buddhist-method).

Revision: `525a52fffa9db11fddfd3e4cb10c58c9efaa4e24`.

The [original MIT license](skills/buddhist-method/LICENSE) credits Udomsak as
the copyright holder. Skill and references: `skills/buddhist-method/`. Original
English/Thai READMEs and pressure-test report: `skills/buddhist-method/`.
Preserve its attribution, terminology, and license when copying the skill.
The README's `nai0om/buddhist-method` installation examples remain unchanged as
upstream material; Suite's actual pin and source are those listed above.

## Agent Plugins schema

`tests/schemas/plugin.schema.json` is copied from the canonical public
https://agent-plugins.org/schemas/1.0.0/plugin.schema.json on 2026-11-07 for offline
validation. It is a reference schema, not authored by Panda Suite. Its canonical
`$id` is retained. The Suite MIT grant does not relicense this reference file.
