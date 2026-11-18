# Panda Release

Panda Release prepares an evidence-based delivery decision: release notes,
readiness assessment, deployment and migration checklists, rollback
considerations, and post-deploy checks for a defined release boundary and target
environment. **Release preparation never authorizes deployment.**

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Deciding whether a change range is ready for an environment, and preparing the artifacts to ship it |
| **Not for** | Deploying, tagging, publishing, applying migrations, or sending announcements (each needs explicit authorization) |
| **Edits by default** | Only requested local documents (for example release notes) |
| **Readiness labels** | READY, CONDITIONALLY READY, BLOCKED, UNKNOWN |
| **Key rule** | "No defects found" is not enough evidence for READY |

## Readiness labels

| Status | Meaning |
| --- | --- |
| **READY** | Scope is known and all required evidence and gates are satisfied |
| **CONDITIONALLY READY** | Named residual risks need an explicit acceptance decision; no mandatory blocker is disguised as optional |
| **BLOCKED** | A mandatory gate fails, or a blocking defect or requirement remains |
| **UNKNOWN** | Evidence is insufficient; the deciding checks are named |

## How it works

1. **Identify scope.** The actual change range and its features, fixes,
   migrations, configuration, dependencies, and docs. Unrelated work and
   unsupported claims are separated out.
2. **Verify contents.** Requirements and acceptance criteria are traced to
   implementation, test evidence, open review findings, and docs. Each check
   records command, environment, revision, and outcome. Evidence from another
   revision does not silently transfer.
3. **Evaluate delivery risk.** Breaking contracts, mixed service versions,
   migrations, data integrity, configuration and access, feature flags,
   integrations, and whether an application rollback still works with changed data.
4. **Define proportional gates.** Tests, defect resolution, review, migration
   rehearsal, configuration, recovery, operational owner, post-deploy checks.
   Sign-off and ownership are never invented; each open gate says whether it blocks.
5. **Produce artifacts.** Release notes, an ordered deployment checklist, a
   migration checklist when relevant, rollback considerations, known issues, and
   post-deploy verification with stop criteria. Commands remain proposed until run.
6. **Assess readiness** using the labels above, with the deciding evidence.

## Examples

### Staging readiness for a branch

```text
$panda-release Prepare the change from origin/main to HEAD for staging. Inspect
the diff, acceptance criteria and available test results. Produce release notes,
deployment/recovery checklists, blockers and post-deploy checks. Classify READY,
CONDITIONALLY READY, BLOCKED or UNKNOWN with evidence. Do not deploy, tag, publish,
apply migrations or send announcements.
```

### Release notes only

```text
$panda-release Write user-facing release notes for v2.4.0 from the commits since
v2.3.0. Save them to docs/releases/v2.4.0.md. Group by feature, fix and breaking change.
```

### Release with a database migration

```text
$panda-release Assess v3.0.0 for production. It includes the orders table
migration in db/migrations/0042. Check whether rolling back the application is
still safe after the migration runs, and include a migration checklist.
```

### Evaluate gates from a plan

```text
$panda-release Evaluate the release gates defined in
.panda-suite/plans/2026-11-12-uuid-migration.md against the current revision and
CI results. Mark each gate passed, failed or missing evidence.
```

Plan defines gates as "evidence pending"; Release assesses them on the actual revision.

### Missing evidence is acceptable input

```text
$panda-release We have no integration test results for this build. Assess
readiness for production anyway and tell me exactly what is missing.
```

Expect UNKNOWN or BLOCKED with the deciding checks named, never READY.

### Post-deploy checklist

```text
$panda-release Write a post-deployment verification checklist for the payments
service with clear stop criteria and rollback triggers.
```

### Handoff for an operator

```text
$panda-release Prepare a delivery handoff for the operations team: scope,
required config changes, ordered steps, known issues and who must approve.
Leave ownership blank where we have not named anyone.
```

## Boundaries

Release does not create or push tags, publish packages, deploy, change
production configuration, apply migrations, or send announcements without
explicit authorization covering those actions. Missing tools mean **Not Run** or
**Blocked**, never a pass. A merged change is not proof of verification or rollout.

## Related

- [Plan](panda-plan.md) for defining release gates ahead of time
- [Release gate planning reference](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-plan/references/release-gates.md)
