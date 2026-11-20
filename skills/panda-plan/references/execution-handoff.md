# Execution handoff

When a plan is saved and implementation is a relevant next step, end the
user-facing response with a request to review the plan and, unless already chosen,
a choice of how `panda-execute` should run it. Put the review/mode request in the
response, not only inside the saved plan:

- **Subagent-driven:** a fresh agent implements each task and a fresh reviewer
  checks it before the next starts, then one whole-change review. Most thorough;
  costs a fresh context per task and review. Offer only when the host can delegate.
- **Native:** this session implements every task, then one review of the whole
  change (by a fresh reviewer when the host can delegate). Cheapest and fastest;
  no independent review until the end.

Recommend one in a sentence grounded in the plan: how many tasks, how much they
depend on each other's interfaces, and what a shipped mistake would cost. Give a
ready-to-use request such as “Use panda-execute (native) to implement
`.panda-suite/plans/<filename>.md`.” When the user already named a mode, keep it
and ask only for the review. When the user asked for a chat-only answer or no
execution, mention the handoff without the menu. Wait for the user's answer:
saving a plan, or choosing a mode in advance, does not by itself authorize
starting implementation unless the user's request already did.

Do not estimate duration without evidence. Planning authorizes the requested plan
artifact, not application implementation. Do not edit source or tests. Do not
require Panda Lead. A handoff to execution preserves acceptance criteria, current
artifacts, decisions, unknowns, and the user's actual authorization; a generated
plan alone is not approval to execute it.
