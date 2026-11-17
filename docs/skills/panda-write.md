# Panda Write

Panda Write produces documentation engineers can use to understand, operate,
and verify the current system: READMEs, developer guides, API guides, runbooks,
architecture explanations, and technical handovers, in English or Thai. It also
reviews and repairs existing documents.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | New docs, updating stale docs, reviewing docs for unsupported claims, DOCX/PDF output from a template |
| **Not for** | Proposed contracts and design ([Spec](panda-spec.md)), observed user journeys ([Manual](panda-manual.md)), marketing copy |
| **Edits by default** | The requested documents only; review-only requests return findings without edits |
| **Saved to** | `.panda-suite/docs/<story-slug>/YYYY-MM-DD-<topic>.md`, unless you give a path, name an existing doc, or ask for chat only |
| **Gaps** | Asks first; uses `Pending Confirmation` only when you allow continuing with gaps |

## Ask before guessing

Every section needs a named source of truth: current code, a document or system
you reference, or your answer. Before drafting, Write asks one precise question
when the source, scope, audience, or content is unclear, sources conflict, or a
material fact is unknown. It writes only what the sources establish and what you
asked for, and asks before adding extra sections or examples.

## How it works

1. **Gather evidence.** Implementation, configuration, schemas, migrations,
   tests, contracts, and existing docs. Each feature or integration is traced on
   its own: similar names do not prove identical behavior. A claim-to-source map
   is kept for material claims.
2. **Define structure** around the reader's task: purpose, prerequisites, steps,
   behavior, troubleshooting, operations, or references as needed.
3. **Draft.** Direct B2-level English, or professional Thai with exact
   identifiers. Implementation, configuration, deployed state, external
   contracts, requirements, and proposals stay separate. No filler, slogans, or
   "there is no X" narration; absences appear only when the reader needs them to act.
4. **Verify claims.** Paths, configuration names, commands, payloads, errors, and
   permissions are checked against source. Safe examples are run where feasible
   and unverified examples are marked.
5. **Refine.** Duplication, unsupported claims, and "limits of this document"
   notes are removed from the artifact and reported in the delivery message instead.

For substantial architecture explanations, integration guides, and handovers,
Write uses its [engineering document guidance](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-write/references/engineering-documents.md),
taking only the relevant sections.

## Formats

- **Markdown** by default.
- **DOCX or PDF** on request, with the Markdown source kept beside it, using
  converters that already exist locally. Nothing is installed without asking.
- **DOCX templates:** page layout, fonts, heading hierarchy, spacing, tables,
  headers, and footers are matched. Template wording is not treated as fact.
- **Diagrams in DOCX:** Mermaid source first, checked against evidence, rendered
  and embedded; the source is kept beside the deliverables.
- **Thai documents:** body paragraphs get a one-tab first-line indent.

## Examples

### Developer guide from source

```text
$panda-write Write docs/approvals-guide.md for new backend developers using the
current src/approvals implementation. Include a runnable example and actual error
behavior. Rejection is only proposed, so do not document it as implemented.
Use clear English. Do not modify application code.
```

### Review an existing README (no edits)

```text
$panda-write Review README.md against the current code. List stale, unsupported
or contradictory claims with line numbers and evidence. Do not edit.
```

### Update a stale document

```text
$panda-write Update docs/deploy.md to match the current Dockerfile and
.github/workflows/deploy.yml. Keep its structure and language.
```

### Runbook

```text
$panda-write Write an on-call runbook for the payment webhook worker: how to tell
it is unhealthy, safe restart steps, and how to replay failed events. Use only
commands that exist in this repository.
```

### API integration guide

```text
$panda-write Write an integration guide for partners calling our /v1/orders API.
Use the OpenAPI file and handlers as the source. Include authentication, one full
request and response, and the actual error codes.
```

### Technical handover in Thai

```text
$panda-write เขียนเอกสารส่งมอบงานภาษาไทยสำหรับระบบ billing จาก src/billing และ
docs/billing ระบุสถาปัตยกรรม การตั้งค่า งานที่ค้าง และความเสี่ยงที่มีหลักฐานรองรับ
```

### DOCX from a company template

```text
$panda-write Create a DOCX architecture overview of the notification service
using templates/company-report.docx for formatting. Include a component diagram.
Keep the Markdown and Mermaid source beside it.
```

### Continue with gaps

```text
$panda-write Write the database operations guide now. The backup schedule is
unknown; continue with gaps and mark it Pending Confirmation.
```

### Chat-only answer

```text
$panda-write Draft a short README section explaining the --dry-run flag. Reply
in chat; do not save a file.
```

## Delivery message

Alongside the artifact you get a short account of the evidence used, what was
actually verified (for example, which example commands ran), and remaining gaps.
Saved files are verified to exist and linked. `.panda-suite/` output is never
staged or committed; Write tells you if Git would track it.

## Boundaries

Writing authorizes documentation changes only. Secret values are omitted; keys
and safe placeholders are documented instead. Deployment, publication,
production data changes, and external side effects need separate authorization.

## Related

- [Write refinement report](../panda-write-refinement.md)
- [Spec](panda-spec.md), [Manual](panda-manual.md), [Learn](panda-learn.md)
