# Saved refactor plans

For a persisted plan, default to `.panda-suite/plans/YYYY-MM-DD-<topic>.md` using
the current local date; honor an explicit destination or chat-only request.
Preserve existing files and ensure root `.gitignore` covers `/.panda-suite/`;
verify with `git check-ignore`. Report already tracked plan artifacts and leave
the index unchanged. Scope a planning-only request to its plan and this ignore
configuration; source and tests remain unchanged.
