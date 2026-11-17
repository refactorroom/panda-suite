# Panda Setup

Panda Setup delivers a usable development starting point: a minimal application
or adapted repository whose documented commands actually work, plus concise agent
instructions and correct ignore rules. Folders, templates, or documentation alone
are not a setup.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Starting a new project, preparing an existing repository for agent-assisted work, auditing setup readiness |
| **Not for** | Feature work on an already configured project ([Execute](panda-execute.md)) |
| **Edits by default** | Reversible edits inside the target project; an audit changes nothing |
| **Versions** | Latest compatible stable release, checked against official sources at setup time |
| **Result labels** | Ready, Partially configured, Audit only |

## Three modes, inferred for you

| Situation | What Setup does |
| --- | --- |
| **New project** (empty or absent destination) | Creates the smallest working app |
| **Existing project** | Keeps its architecture, dependencies, package manager, lockfiles, and config; adds what is missing. Upgrades and migrations are proposed, never applied silently |
| **Readiness audit** ("audit", "inspect", "do not change") | Reports gaps and proposed edits; changes nothing |

You do not need to name a mode or learn command syntax.

## How it works

1. **Inspect before asking.** AGENTS.md and files it references, host-specific
   files, manifests, lockfiles, version pins, layout, scripts, CI, `.gitignore`,
   Git status.
2. **Resolve material requirements.** Only questions that change the setup:
   what you build, backend/frontend/both, frameworks, destination, module name,
   persistence/auth needs, agent hosts, conventions. Each comes with two or three
   plain choices and a recommendation.
3. **Select stack and versions** from official documentation or package metadata
   at setup time. Never a prerelease unless requested; never an upgrade of an
   existing app unless asked. A remembered version is labeled unverified.
4. **Create or adapt the smallest working structure.** Databases, auth,
   containers, queues, or deployment config only when required.
5. **Configure the agent harness.** Create or reconcile AGENTS.md (and a
   host-specific file if selected), describing only commands and paths that exist.
6. **Configure ignore rules.** Local secrets, build output, caches, and
   `/.panda-suite/` are ignored; `.env.example` stays tracked. Verified with
   `git check-ignore`.
7. **Verify and report.** Install, build, type check, lint, a meaningful test,
   and a smoke request or page load. Only a project that passes every applicable
   check is called **Ready**.

## Readiness checks

| Check | Evidence |
| --- | --- |
| Dependencies resolve | Install exits 0; lockfile present |
| Build | Build or ecosystem check (for example `go build ./...`, `go vet ./...`) |
| Type check | `tsc --noEmit` or equivalent, or "not applicable" with a reason |
| Lint | The configured linter runs |
| Meaningful test | At least one real test passes; an empty suite does not count |
| Smoke | Start the app, request the documented endpoint or page, observe the expected result, stop it |
| Instructions match | Every command and path in AGENTS.md was run or exists |
| Ignore rules | `git check-ignore` in both directions |
| No secrets | Tracked files hold placeholders only |

Each check is reported as **passed**, **failed**, **not run**, or **blocked**.

## Examples

### New Go backend

```text
$panda-setup Initialize a Go + Fiber backend in ./api with a health endpoint.
```

### Full-stack repository

```text
$panda-setup Set up a React frontend and Go backend in one repository.
```

### Prepare an existing project

```text
$panda-setup Prepare this existing project for Panda Suite.
```

Expect AGENTS.md reconciled with real commands, the `/.panda-suite/` ignore
rule, and verified checks. The stack is not changed.

### Readiness audit only

```text
$panda-setup Audit this repository's setup readiness. Do not change files.
```

### Python API with a database

```text
$panda-setup Create a FastAPI service in ./service with PostgreSQL via
docker compose, one /health route and one tested repository function. Use the
latest stable versions and show where each version came from.
```

### Frontend only

```text
$panda-setup Create a Vue + Vite frontend in ./web with TypeScript, a lint
config and one component test.
```

### Next.js app

```text
$panda-setup Initialize a Next.js app in ./site using the official generator.
Use npm. Add an AGENTS.md for Codex and Claude Code.
```

### A stack without a stack note

```text
$panda-setup Initialize a Rust + Axum service in ./svc with a health route.
```

Any stack works: Setup finds the official setup path at run time. Stack notes
(Go + Fiber, Fastify, FastAPI, React/Vue + Vite, Next.js) only add pitfalls
already observed.

### Resume after a failure

```text
$panda-setup Continue the setup in ./api. The previous run failed because Go was
not installed; it is installed now.
```

Running setup again keeps customizations and adds no duplicates.

## Boundaries

A setup request authorizes project-local source, dependency installation into the
project, agent instruction files, `.gitignore`, example env files, and local
checks. It does not authorize commits, pushes, deployment, global tool
installation, global host configuration, real credentials, paid services,
deleting your files, or rewriting the Git index. A missing toolchain gets the
exact install command, not a global install.

## Related

- [Setup design and evaluation](../panda-setup.md)
- References: [discovery and versions](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-setup/references/discovery-and-versions.md),
  [agent harness](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-setup/references/agent-harness.md),
  [combined projects](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-setup/references/combined-projects.md),
  [readiness](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-setup/references/readiness.md)
