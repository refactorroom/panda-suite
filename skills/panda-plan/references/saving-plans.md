# Saving plans in Git

When saving a plan inside `.panda-suite` in a Git repository, ensure the
repository root `.gitignore` ignores `/.panda-suite/`. Create the file if needed,
preserve existing entries, and avoid adding a duplicate when an existing rule
already covers the directory. Verify the intended plan path with `git check-ignore`.
Ignore rules do not remove files already tracked by Git; report any tracked
`.panda-suite` files and leave the index unchanged. If the ignore rule cannot be
updated or verified, report that limitation. Respect an explicit request to track
the plan or a repository instruction requiring it.
