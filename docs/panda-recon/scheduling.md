# Scheduled intelligence refresh (optional)

Nothing is scheduled by default. Panda Recon does not install a scheduler, run a
daemon, send alerts or claim continuous monitoring. Use this page only if you want
the intelligence cache refreshed without asking an agent each time. Every command
here is an illustrative setup for you to review and install yourself.

## What a scheduled run does

`intel update` contacts the fixed public endpoints in the
[source registry](../../skills/panda-recon/assets/intelligence-sources.json): NVD,
CISA KEV, the three OWASP pages and the MITRE ATT&CK index. It writes dated
snapshots to the private cache. It sends no source code, paths or tokens. Package
names and versions go to OSV only when you add `--allow-package-queries` and a
component inventory.

Each run fetches every selected source. It does not skip sources whose cache is
still fresh. To check OWASP and ATT&CK only weekly, schedule them separately with
`--source`.

Missed runs catch up: NVD resumes from the last successful sync (minus two
minutes). A gap longer than 120 days is refused and needs a manual partitioned
refresh. A failed source keeps its previous snapshot, and the run exits 3.

## Local scheduler (cron)

Run from the Suite checkout so the default cache
`.panda-suite/recon/intelligence-cache` is used. Example crontab entries:

```text
# Daily at 06:00: KEV and NVD changes
0 6 * * * cd /path/to/panda-suite && .venv/bin/python skills/panda-recon/scripts/recon.py intel update --source kev --source nvd --allow-network >> .panda-suite/recon/intel-update.log 2>&1
# Mondays at 06:30: OWASP and ATT&CK versions
30 6 * * 1 cd /path/to/panda-suite && .venv/bin/python skills/panda-recon/scripts/recon.py intel update --source owasp-web --source owasp-api --source owasp-asvs --source mitre --allow-network >> .panda-suite/recon/intel-update.log 2>&1
```

On macOS, launchd works the same way with the same command. Check results at any
time without network access:

```sh
.venv/bin/python skills/panda-recon/scripts/recon.py intel status --offline
```

Exit 0 means every enabled source is fresh. Exit 3 means at least one is stale,
unavailable or failed; `sourceStatus` says which and why.

## Project exposure summary

To also check a project's npm dependencies, add the inventory and the separate
package permission. Reports need a new directory each run:

```text
0 7 * * * cd /path/to/panda-suite && .venv/bin/python skills/panda-recon/scripts/recon.py intel latest --allow-network --allow-package-queries --project /path/to/project --output .panda-suite/recon/reports/intel-$(date +\%Y\%m\%d) >> .panda-suite/recon/intel-update.log 2>&1
```

Reports stay in the private `.panda-suite/` directory. Nothing is published,
emailed or used to upgrade dependencies. Review them before sharing.

## GitHub Actions

A scheduled workflow can run the same commands, but consider privacy first: a
workflow on a public repository exposes its logs, and caches or artifacts can
reveal your dependency list. If you use one, keep the repository private, grant
`permissions: contents: read` only, do not upload reports as public artifacts,
and do not let the workflow open pull requests or upgrade packages automatically.
Panda Suite ships no such workflow.

## Known limits

- **NVD change volume:** the helper reads at most 3 pages of 100 changed NVD
  records per run. Real NVD activity is often far higher (1,440 records changed in
  one day on 2026-11-17), so NVD in `intel update` and `intel latest` is usually
  reported Unavailable against the live service. KEV, EPSS, OWASP, MITRE and
  single `intel cve` lookups are not affected. Until this is fixed, schedule
  `--source kev` and use `intel cve` for specific CVEs.
- Duplicate alert suppression is not provided because no alerts are sent.
- Unauthenticated NVD requests are rate limited; the helper retries with backoff
  and respects Retry-After, but frequent schedules make failures more likely.
