# Subagent-driven execution

For each task, give a fresh implementer only that task's
text, its interfaces note, the plan's constraints, and the relevant paths.
Re-run the task's checks yourself; a subagent's report is not evidence. Then
give a fresh reviewer the task, the plan's acceptance criteria, and the diff;
fix material findings before the next task. Run tasks that touch the same
files one at a time. Finish with one whole-change review.
