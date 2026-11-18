# Panda Spec

Panda Spec writes implementation-oriented specifications (backend, frontend,
API, database, integration, architecture, RFC, or ADR) from requirements and
source evidence, in professional English or Thai. It never presents proposed
behavior as already implemented.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Defining contracts and design that must hold: interfaces, data models, errors, permissions, failure behavior |
| **Not for** | A usage guide ([Write](panda-write.md)), ordered tasks ([Plan](panda-plan.md)), user steps ([Manual](panda-manual.md)) |
| **Edits by default** | Only the spec artifact |
| **Saved to** | `.panda-suite/specs/YYYY-MM-DD-<topic>.md` in the active project, unless you give a path or ask for chat only |
| **Languages** | English or professional technical Thai, with exact code names |

## Labels used in every spec

| Label | Meaning |
| --- | --- |
| **Current** | Supported by inspected source or contracts |
| **Proposed** | New design, not yet approved or implemented |
| **Open decision** | A choice that needs an owner; the spec says whether it blocks implementation |

## How it works

1. **Inspect requirements and current behavior.** Entry points, callers, data
   flow, and invariants, with source locations for material claims.
2. **Identify contracts and constraints.** Interfaces, data models, database
   constraints, transactions, errors, permissions, dependencies, async work, and
   operational behavior where relevant. Missing source is an evidence gap, never a
   license to invent a route, schema, or payload.
3. **Define the design** with the labels above, covering compatibility, failure
   behavior, consistency, migrations, deployment and recovery, performance, and
   testing as the change needs.
4. **Validate.** The spec is reconciled with source and requirements; examples
   and cross-references are checked; proposed tests are kept separate from
   executed checks.

For substantial specs, a [section menu](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-spec/references/specification.md)
is used selectively. Your own template wins when supplied.

## File handling

- Requirements, source, and templates are inputs. If "write a spec for the
  policy in requirements.md" could mean editing that file, Spec asks first.
- A named existing spec is edited in place.
- In a multi-project workspace, the request or its sources pick the project;
  Spec asks if several still fit.
- Finished documents contain no conversational questions; decisions are collected
  in their own section.

## Examples

### Thai backend specification

```text
$panda-spec เขียน Backend Technical Specification ภาษาไทยจาก
docs/approval-requirements.md และ src/approvals ใช้ template ของโครงการ
แยกพฤติกรรมปัจจุบัน ข้อเสนอ และประเด็นที่ยังต้องตัดสินใจ
ระบุ interface, validation, permission, error และ test strategy เท่าที่มีหลักฐาน
บันทึกที่ docs/approval-spec.md โดยไม่แก้ application code
```

### API contract in English

```text
$panda-spec Write an API specification for the proposed POST /v2/refunds
endpoint from docs/refund-requirements.md. Include request and response schemas,
validation, permission rules, error codes, idempotency, and examples. Mark
everything not in source as proposed.
```

### Database design

```text
$panda-spec Specify the schema change for multi-currency invoices: tables,
constraints, indexes, migration and backfill, and rollback limits. Use
db/migrations and src/models/invoice.py for current state.
```

### Architecture Decision Record

```text
$panda-spec Write an ADR for choosing between Postgres LISTEN/NOTIFY and a
message broker for order events. Include context, options, decision status,
consequences and revisit conditions. The decision is not yet approved.
```

A recommendation is never recorded as stakeholder approval.

### Frontend specification

```text
$panda-spec Specify the checkout form's client-side validation, loading and
error states, and accessibility requirements, based on src/web/checkout and the
API contract in docs/api.md.
```

### Integration specification

```text
$panda-spec Specify how we integrate with the payment provider's webhooks:
signature verification, retries, ordering, duplicate delivery and failure
handling. Use the provider's official documentation for its guarantees.
```

External guarantees come from the provider's contract, not from local callers.

### Update an existing spec

```text
$panda-spec Update docs/specs/search-spec.md: the team decided to drop fuzzy
matching. Apply the decision throughout and keep the rest unchanged.
```

### RFC with open decisions

```text
$panda-spec Draft an RFC for per-tenant rate limits. We have not decided the
limits or the storage backend. Keep those as open decisions and state whether
each blocks implementation.
```

## Boundaries

Spec edits the requested spec only. Implementation and external actions need
separate authorization. A useful spec can contain open decisions; they are never
hidden behind invented detail.

## Related

- [Requirements](panda-requirements.md) for the rules a spec builds on
- [Plan](panda-plan.md) to order the implementation of a spec
