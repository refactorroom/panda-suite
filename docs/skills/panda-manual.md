# Panda Manual

Panda Manual documents what a user can actually do. It creates user and
administrator manuals, onboarding guides, and feature walkthroughs from observed
application journeys or supplied UI evidence, capturing screenshots with a
browser when one is available. A hypothetical UI is never presented as an observation.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | End-user and admin manuals, onboarding guides, feature walkthroughs |
| **Not for** | Developer implementation detail ([Write](panda-write.md)), design contracts ([Spec](panda-spec.md)) |
| **Edits by default** | The manual artifact and its captures |
| **Browser** | Optional; discovered at run time, never assumed |
| **Evidence labels** | observed, documented but not observed, unverified |

## How it works

1. **Inspect the starting state.** Environment, role, route, and evidence
   source are recorded without secrets.
2. **Navigate the bounded journey.** Each state is observed before the next
   action. Actual labels, inputs, prerequisites, and expected versus observed
   outcomes are recorded. Safe validation and recovery paths are observed when feasible.
3. **Capture screenshots** only when supported and useful, with descriptive
   names such as `02-draft-saved.png`. Sensitive information is excluded or
   redacted. A supplied screenshot keeps its own provenance.
4. **Write** prerequisites, numbered steps, expected outcomes, observed errors
   and recovery, and evidence status, using exact UI labels and the reader's language.
5. **Recheck** the sequence against the observations. Consequential actions are
   not repeated just to verify documentation.

Without browser access, Manual produces a clearly labeled **draft from supplied
evidence** and names the smallest check needed to complete it.

## What to provide

- The application URL (a test environment is preferred) or screenshots/specs.
- The role and journey to document.
- Language and output location.
- Which actions are permitted (for example: no sending, publishing, or deleting).

## Examples

### Observed walkthrough with screenshots

```text
$panda-manual Document saving a draft at http://127.0.0.1:8765 for a test user.
Observe actual labels and outcomes; capture useful screenshots with synthetic
data. Save docs/draft-manual.md. Do not send messages, publish or delete records.
If the browser is unavailable, make a labeled draft from supplied evidence only.
```

### Administrator guide

```text
$panda-manual Write an admin guide for inviting users and assigning roles in the
staging app at https://staging.example.test. Use the test admin account from
fixtures/users.json. Do not invite real email addresses.
```

### Onboarding guide in Thai

```text
$panda-manual เขียนคู่มือเริ่มต้นใช้งานภาษาไทยสำหรับผู้ใช้ใหม่ ตั้งแต่สมัครบัญชีจนสร้างโปรเจกต์แรก
ที่ http://localhost:3000 ใช้ข้อมูลทดสอบเท่านั้น และบันทึกภาพหน้าจอประกอบแต่ละขั้น
```

### Draft from supplied evidence only

```text
$panda-manual There is no running app. Use the screenshots in design/export-flow/
and docs/export-spec.md to draft a user guide for exporting reports. Label every
step's evidence status.
```

Expect "documented but not observed" labels and no invented validation messages.

### Validation and error paths

```text
$panda-manual Document the sign-up form at http://localhost:3000/signup,
including what users see for an invalid email and a weak password, and how to recover.
```

### Feature walkthrough for release notes

```text
$panda-manual Write a short walkthrough of the new bulk edit feature for the
release announcement. Observe it on the local build; three steps maximum.
```

### Update an existing manual

```text
$panda-manual The settings page was redesigned. Update docs/user/settings.md to
match the local build, replace outdated screenshots, and list steps that no
longer exist.
```

## Boundaries

Production-data interaction, deletion, payments, messaging, publication, and
other external side effects need authorization covering them. A walkthrough
does not grant access to another role or account.

## Related

- [Browser-observed example manual](../../tests/results/browser-manual/manual.md)
- [Manual structure reference](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-manual/references/manual.md)
