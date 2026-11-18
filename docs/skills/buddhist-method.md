# Buddhist Method

Buddhist Method encodes Buddhist epistemic and decision principles as practical
work disciplines. Each one targets a failure mode that both models and people
fall into: trusting a remembered fact, patching a symptom, acting on stale
state, defending a weak draft, or giving way to pressure. The Pali and Thai names
are kept as short memory keys; no belief is required.

## At a glance

| Topic | Summary |
| --- | --- |
| **Use it for** | Verifying a claim before stating it, a stubborn bug, a hack-or-fix decision, pushback, long multi-step tasks |
| **Not used as** | A mandatory stage between every activity; [Lead](panda-lead.md) loads it only at a specific uncertainty or pressure point |
| **Edits by default** | None by itself; it shapes judgment within the current task's authorization |
| **Main output** | Evidence-based judgment with visible uncertainty, not a philosophical report |

## The six core principles

| Situation | Principle | Discipline |
| --- | --- | --- |
| About to state a fact, API, flag, or version from memory | **Kalāma** (กาลามสูตร) | Verify from a source you just consulted, or state the limit of your knowledge |
| A bug appears and the first instinct is a try/catch | **Yoniso Manasikāra** (โยนิโสมนสิการ) | Name at least three plausible causes before fixing anything |
| Acting on state from earlier in a long task | **Sati-Sampajañña** (สติ-สัมปชัญญะ) | Re-check the actual file, value, or result before acting |
| New evidence makes your draft look wrong | **Anatta** (อนัตตา) | Ask what you would propose if you had not written it; rewrite freely |
| Choosing between a workaround and a real fix | **Pahāna** (ปหานะ) | Remove the cause, or label the workaround as a known gap |
| Pushback, repeated tool failure, urge to over-correct | **Upekkhā** (อุเบกขา) | Change direction only when the evidence changes, not the pressure |

## How the principles combine

- **A bug appears:** Yoniso (find the cause), then Pahāna (remove it).
- **Stating a fact:** Kalāma (verify); if still uncertain, say so plainly.
- **Strong pushback:** Upekkhā (hold steady), Kalāma (re-verify), and if you were
  wrong, Anatta (rewrite, don't patch).
- **Long task:** Sati throughout, Yoniso when something breaks.
- **Hard, fuzzy problem:** the Four Noble Truths frame in
  [ariyasacca-debug](https://github.com/refactorroom/panda-suite/blob/dev/skills/buddhist-method/references/ariyasacca-debug.md).

## Extended principles

Read [extended principles](https://github.com/refactorroom/panda-suite/blob/dev/skills/buddhist-method/references/extended-principles.md) when:

| Situation | Principle |
| --- | --- |
| Discipline slipping late in a long task | Appamāda (heedfulness) |
| Large or dragging task | Iddhipāda 4 (four bases of accomplishment) |
| Tempted to deliver a stub or "rest unchanged" | Kusala-dhamma-chanda (deliver the whole artifact) |
| Same approach retried more than twice | Apāyakosalla (recognize decline) |
| Quick hack versus proper fix | Atthatraya (short- versus long-term benefit) |
| Unclear audience or whether to ask | Sappurisadhamma |
| Over- or under-engineering | Majjhimā Paṭipadā (middle way) |
| Structural choice (schema, signature, payload) | Anāgataṃsa-ñāṇa (bounded foresight) |
| A test just failed and you want to guess a fix | Pariññā (write out what executed, what failed, and why first) |
| The user's message carries strong emotion | Brahmavihāra (match the register) |

## Examples

### Verify a claim before publishing it

```text
$buddhist-method Check the claim that approve() persists to PostgreSQL before
we describe it in release notes. Inspect the source and actual test evidence.
Separate established behavior from assumptions. Do not change code.
```

### Stubborn bug after several attempts

```text
$buddhist-method We have tried three fixes for the flaky login test and none
worked. Stop guessing: list the plausible causes and the observation that would
distinguish them.
```

Expect Yoniso Manasikāra and Apāyakosalla: reassess the approach rather than a
fourth blind retry.

### Hack or real fix?

```text
$buddhist-method I want to wrap the null error in the invoice job with a
default value so the job stops failing. Is that a fix or a patch?
```

Expect a Pahāna judgment: find what produces the null, or surface the workaround
as a documented known gap.

### Holding a position under pushback

```text
$buddhist-method I disagree with your review finding about the race condition.
Are you sure?
```

Expect the evidence re-checked. The finding is withdrawn only if the evidence
changes, and you are asked what new information you have.

### Discard a weak draft

```text
$buddhist-method The design doc you drafted assumed one region; we now run in
three. Should we patch it or start over?
```

### Long task discipline

```text
$buddhist-method Before you continue the migration, re-check the actual state
of the files you changed earlier instead of relying on memory.
```

### Scope check

```text
$buddhist-method Am I over-engineering this? I'm adding a plugin system for a
CLI with two commands.
```

Expect a Majjhimā Paṭipadā assessment tied to demonstrated needs.

### Combined with another skill

```text
$panda-debugger Investigate the duplicate charge bug. Use buddhist-method if the
evidence points in more than one direction.
```

Other skills consult it optionally at a decision point.

## Related

- [Craft](panda-craft.md) uses the Iddhipāda disciplines as working guidance
- [Debugger](panda-debugger.md), [Simplify](panda-simplify.md), [Skill Lab](panda-skill-lab.md) reference individual principles
