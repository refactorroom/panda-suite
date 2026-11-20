# Pre-commit inspection

Preserve unrelated edits and existing staging. Use explicit paths or hunks rather
than blind `git add .`. Before committing, inspect the exact proposed index and
check paths, file sizes, ignore rules and file contents for sensitive material.

Do not commit a file over 10 MiB without explicit user confirmation naming that
file. Report its path and size and pause before staging or committing it. Treat
the threshold as a review trigger, not proof that smaller files are safe.

Never include a detected secret or credential (for example, a populated `.env`,
private key, token, password or credential store) in a commit. Keep it out of the
index, do not print its value, and tell the user the path and type of concern. Ask
the user how to proceed; confirmation to commit does not make a secret safe to
publish. For sensitive configuration or credential-like files whose contents or
purpose are uncertain, exclude them and request explicit path-specific confirmation
before including them. Do not expose values when summarizing the concern.

Check proposed files against applicable `.gitignore` rules and review whether
unignored generated, local, cache, build, data, or environment-specific files
appear to belong there. List each such candidate with a short reason and ask the
user to confirm its inclusion before committing it. Do not add or force-add these
files while confirmation is pending. Existing tracking or staging is not consent.

Also inspect intended content for unrelated changes; redact sensitive findings in
output. Do not claim this is a comprehensive secret scan. Run normal hooks; diagnose
a failure before a bounded retry and never bypass hooks without explicit permission.
Avoid raw remote URLs or configuration dumps that could disclose credentials.
