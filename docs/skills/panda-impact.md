# Panda Impact

Panda Impact assesses a proposed change **before** it is implemented: which
components depend on it, what business behavior and stored data it touches, the
rollout risks, and the verification it needs. It is read-only by default.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | API or schema changes, renaming fields, replacing a library, moving a module, changing an event shape |
| **Not for** | A defect investigation ([Debugger](panda-debugger.md)), a migration execution plan ([Plan](panda-plan.md)), an ordinary diff review ([Review](panda-review.md)) |
| **Edits by default** | None, apart from an analysis document you request |
| **Main output** | Confirmed dependencies, affected components, data/API/behavior impact, operational risks, compatibility assessment, mitigations, verification, unknowns |

## Confidence labels

| Label | Meaning |
| --- | --- |
| **Confirmed impact** | A demonstrated dependency plus an incompatible change |
| **Likely impact** | Evidence fits, but a key boundary is unverified |
| **Possible risk** | A plausible condition that has not been tested |
| **Unknown** | Evidence cannot decide |

Each finding states its consequence, trigger, evidence, missing check, and
priority. A matching identifier alone does not prove an affected runtime path.

## How it works

1. **Bound the change.** Old and new contract, affected versions and
   environments, expected benefit, scope. The target stays "proposed" until approved.
2. **Trace dependencies.** Producers and consumers through callers, models,
   queries, serializers, UI, jobs, events, integrations, configuration, and tests,
   with precise paths. Each negative search is bounded by its scope.
3. **Assess boundaries.** Stored-data compatibility, request/response and event
   contracts, validation and errors, deployment ordering, mixed versions,
   background work, monitoring, and recovery. Code-defined schema is kept separate
   from observed database contents.
4. **Classify findings** with the labels above.
5. **Recommend mitigation.** The least complicated compatible approach, with
   tests, consumer coordination, migration and rollout checks, observability, and
   rollback limits. A lossy conversion may need a backup restore rather than a
   reverse script; reversibility is never promised without evidence.
6. **Validate coverage.** Every material impact has a mitigation or explicit
   decision, and uninspected repositories, consumers, or data are named.

## What to provide

- The exact proposed change (old and new shape).
- The repositories, contracts, or schemas available for tracing.
- Known external consumers, if any.

## Examples

### Change a field's type

```text
$panda-impact Analyze replacing order_status strings with integer codes. Trace
models, queries, API responses, UI callers, jobs and tests that actually exist.
Separate confirmed dependencies from possible external consumers and unknowns.
Assess compatibility, migration/recovery risks and required verification. Read-only.
```

### Rename a public API field

```text
$panda-impact We want to rename "customerId" to "accountId" in the public
REST API. What breaks, which clients might be affected, and what compatibility
options exist (aliasing, versioning)? Read-only.
```

### Split a table

```text
$panda-impact Assess splitting the users table into users and profiles.
Include ORM models, raw SQL, reports, background jobs and fixtures. Note
deployment ordering for mixed application versions.
```

### Replace a dependency

```text
$panda-impact What is affected if we replace moment.js with date-fns? List every
call site and any behavior differences (time zones, parsing) that could change output.
```

### Change an event payload

```text
$panda-impact We plan to drop the "legacy_total" field from the OrderPlaced
event. Trace producers and consumers in this repository and list the consumers
we cannot see.
```

Expect "Unknown" for consumers outside the inspected repositories, with the
smallest observation that would resolve it.

### Configuration default change

```text
$panda-impact What happens if we change the default session timeout from 30
days to 7 days? Include mobile clients, remember-me tokens and support load.
```

### Save the assessment

```text
$panda-impact Assess moving file uploads from local disk to object storage.
Save the analysis to docs/upload-storage-impact.md with a small dependency diagram.
```

## Boundaries

Impact does not edit source, run migrations, modify data, or trigger deployment
or external effects unless separately authorized. Missing consumer or production
access lowers confidence; it never proves that no consumer or stored record exists.

## Related

- [Plan](panda-plan.md) to turn the mitigations into tasks and release gates
- [Spec](panda-spec.md) to define the new contract precisely
