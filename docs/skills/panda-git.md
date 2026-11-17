# Panda Git

Panda Git inspects the actual changes before it chooses a commit type or touches
history. It owns Git operations and commit conventions: commit messages, commit
reviews, scoped commits, conflicts, branches, history, and recovery. A coding
task alone does not authorize a commit.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Commit messages, commit proposals, creating scoped commits, conflict resolution, history inspection and recovery |
| **Not for** | Code review (use [Review](panda-review.md)), release readiness ([Release](panda-release.md)), deployment |
| **Edits by default** | None. `$panda-git commit` is a proposal; an explicit "create the commit" request executes it |
| **Default convention** | Conventional Commits, after your explicit instructions and the repository's own rules |
| **Never without explicit request** | `--amend`, history rewrite, push, tag, hook bypass, destructive cleanup |

## Operations

| Request | What happens |
| --- | --- |
| **Message only** | Reads the diff and relevant source, returns a message, changes no Git state. A message from a description alone is labeled provisional. |
| **Commit review** (`$panda-git commit`) | Proposes the complete message, intended paths and file count, type/scope rationale, breaking changes, verification evidence and risks. Ends with "Proposal only; no commit performed." |
| **Commit execution** | Stages only intended paths or hunks, inspects the whole index, commits, then verifies the result. No second confirmation for an already authorized scope. |
| **Conflicts** | For an authorized merge, rebase, or cherry-pick: preserves both sides' requirements; semantic conflicts need your decision. |
| **Branches, history, recovery** | Inspects topology and preserves recoverable state before any authorized rewrite. |

## Commit message format

```text
<type>(<optional scope>)<optional !>: <subject>

<optional body>

<optional footers>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`,
`ci`, `build`, `revert`, and `wip` (only when allowed). The type comes from the
change's intent and actual diff, never from file names. Tests that accompany a
fix belong to `fix`. Removing supported output or an option is a behavior change,
so it is not `refactor` even with `!`. Panda's defaults: header at most 72
characters, lines at most 100, imperative lowercase subject, no trailing period.

## Safety checks before any commit

- Stages explicit paths or hunks, never a blind `git add .`.
- Preserves unrelated edits and staging that belong to someone else.
- Pauses on any file over 10 MiB until you confirm that specific file.
- Keeps detected secrets (a populated `.env`, private keys, tokens) out of the
  index, reports the path and type without printing the value, and asks how to
  proceed.
- Lists generated, cache, build, or local files that are not ignored and asks
  before including them.
- Runs normal hooks; a hook failure is diagnosed, never bypassed without your
  permission.

This is a careful review, not a guaranteed secret scan.

## After a commit

Git checks `git status --short`, `git log -1 --format=fuller`, and
`git show --stat --oneline HEAD`, then reports the hash, full message, checks
that ran, and changes that remain.

## Examples

### Propose a commit (no execution)

```text
$panda-git commit
```

Expect a full proposal and "Proposal only; no commit performed."

### Create a scoped commit

```text
$panda-git Create a commit for the auth change and its tests. Leave my notes alone.
```

Explicit authorization: Git stages only the auth files and tests, commits, and
verifies the result.

### Message only, for a staged change

```text
$panda-git Write a commit message for what is staged. Do not commit.
```

### Split mixed work

```text
$panda-git I changed the export format and also fixed a typo in the README.
Propose how to split this into commits, with a message for each. Do not commit yet.
```

Expect a recommendation to separate the two purposes, with intended paths and a
message per commit.

### Follow a repository convention

```text
$panda-git Commit the billing fix using our commitlint rules and the
"billing" scope. Include the issue footer "Refs: BILL-412".
```

Your explicit convention wins over the default. Repository hooks still apply.

### A breaking change

```text
$panda-git Propose a commit for removing the --legacy flag from the CLI.
Explain whether it is breaking and how the message should show it.
```

Expect a type that matches the real intent, a `!` marker and/or a
`BREAKING CHANGE:` footer, and the evidence for that classification.

### Resolve a merge conflict

```text
$panda-git Resolve the conflicts from merging main into feature/invoices.
Keep both the new tax rule from main and our rounding change. Ask me if they
contradict. Do not push.
```

Expect a resolution that preserves both sides' requirements, or a precise
question when the two rules conflict semantically.

### Recover lost work

```text
$panda-git I ran a hard reset and lost my last two commits. Find them and
restore them to a new branch called recover/invoices. Do not change main.
```

Expect inspection of the reflog and a new branch at the recovered commit,
verified with the relevant log output.

### Inspect history only

```text
$panda-git Show which commits since v1.7.0 touched the installer, grouped by
type. Read-only.
```

### Combined delivery

```text
$panda-git Commit the docs changes and push this branch to origin.
```

Push authority is separate from commit authority. Here both are explicitly
requested, so both are performed and each is verified.

## Tips

- "Commit my code" means a new commit, never an amend.
- If a fix is needed before a safe commit, Git reports the issue and asks
  whether to fix it. It does not silently change your code.
- Other Panda skills (Execute, Refactor, Craft) load this guidance when their
  authorized work reaches Git.

## Related

- [Contract and evaluation](../panda-git.md)
- References: [commit conventions](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-git/references/commit-conventions.md),
  [conflict resolution](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-git/references/conflict-resolution.md),
  [history and recovery](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-git/references/history-and-recovery.md),
  [repository inspection](https://github.com/refactorroom/panda-suite/blob/dev/skills/panda-git/references/repository-inspection.md)
