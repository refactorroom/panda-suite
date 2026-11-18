# Panda Invaris

Panda Invaris helps you inspect, author, run, and interpret
Invaris harnesses: configured project checks,
guardrail challenges, mutations, and campaigns. Use it when you need evidence
that your project's checks run, or that they actually detect a specific
deliberate change.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Explaining a harness, running checks, testing whether a guard detects a violation, testing whether tests catch a code change |
| **Not for** | General test design ([Test](panda-test.md)), agent or skill evaluation ([Evaris](panda-evaris.md)) |
| **Requires** | An installed, compatible Invaris CLI to execute anything; inspection works without it |
| **Edits by default** | None; authoring or running needs your request |
| **Key rule** | A passing check or baseline does not prove a guard detects violations |

## Actions

| Action | What it answers |
| --- | --- |
| `check` | Do the configured guards pass? |
| `run` | Do the steps and guards pass? |
| `challenge` | Does a guard detect a specified violation? |
| `mutate` | Do the selected tests detect a specified code change? |
| `campaign` | What is the aggregate result of defined experiments under a policy? |

The skill checks the installed CLI's version and usage first and does not assume
a newer command or schema is supported.

## How it works

1. **Establish outcome and authorization:** explain only, author or edit a
   harness, or run specific checks. The harness, its commands, paths, policies,
   and side effects are inspected before anything runs. Commands run with your
   permissions; temporary workspaces do not isolate external services.
2. **Check the CLI** and matching documentation and schema. If Invaris is
   missing, the prerequisite is described and inspection continues. `init` can
   create an empty harness, which is not verification by itself.
3. **Choose and run** the action that answers the request, reporting the actual
   command, harness, version, exit status, and evidence.
4. **Interpret the native report** without flattening it: strong structured
   proof versus legacy marker evidence; PROVEN, UNPROVEN, INCONCLUSIVE; KILLED,
   SURVIVED, INVALID, INCONCLUSIVE. Exit 2, missing tools, timeout, refusal, or
   invalid evidence is never a pass. Mixed or incomplete campaign results are preserved.
5. **Evaris integration**, if requested, follows Evaris's current compatibility
   contract. An Invaris ACCEPT never proves task completion.

## Examples

### Explain a harness

```text
$panda-invaris Inspect .invaris/invaris.json and explain which guard checks
access control. Run the authorized challenge and report its actual evidence.
```

### Explain only

```text
$panda-invaris Explain what each guard in .invaris/invaris.json does and what
side effects running it could have. Do not run anything.
```

### Run the checks

```text
$panda-invaris Run check with the project harness and summarize each guard's
result with the native evidence path.
```

### Does the guard catch a violation?

```text
$panda-invaris Challenge the "no secrets in config" guard with a synthetic fake
API key in a temporary copy. Report PROVEN, UNPROVEN or INCONCLUSIVE.
```

### Do the tests catch a code change?

```text
$panda-invaris Mutate src/auth/owner.py by removing the owner comparison and run
the auth tests. Report KILLED or SURVIVED with evidence.
```

A SURVIVED mutation shows a test gap worth handing to [Test](panda-test.md).

### Author a harness

```text
$panda-invaris Create a harness for this Node project with guards for lint,
type check and unit tests, using the commands in package.json. Validate it with
doctor if this Invaris version supports it.
```

### Campaign

```text
$panda-invaris Run the campaign in .invaris/campaign.json and summarize results,
keeping incomplete and ineligible experiments visible.
```

### Missing CLI

```text
$panda-invaris Run the harness checks.
```

If Invaris is not installed, expect the missing prerequisite to be named and no
invented results. Nothing is installed without authorization.

## Boundaries

Untrusted commands are not run. Existing configuration and your changes are
preserved. Reports are never changed and guards are never weakened to produce a
passing result.

## Related

- [Evaris](panda-evaris.md) for agent and skill evaluations
- [Security](panda-security.md) audits harness evidence paths in `skills` mode
