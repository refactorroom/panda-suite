# Troubleshooting

| Symptom | Check and correction |
| --- | --- |
| Skill absent | Confirm the selected host directory/plugin inventory, complete copied references and supported metadata. Refresh host; avoid duplicate copies. Discovery is not model execution. |
| Unknown mode/option or missing argument | Run helper `help` / `help MODE` or `--help`. Use the four mode names (hunt, incident, verify, intel); scan, recon, simulate and bounty belong to panda-red. |
| Invalid target | Use an existing authorized evidence file or directory; no linked roots or parent-scope fallback. |
| Permission denied | Respect the denied root/output; choose an authorized accessible destination. Do not elevate privileges or broaden scope automatically. |
| Missing case evidence | Keep Not tested/Inconclusive. Restore authorized original bytes or identify collection gaps; never change a hash to manufacture a match. |
| Active check needed | panda-blue never contacts targets. Hand the hypothesis and case ID to panda-red, which requires an engagement first. |
| Helper dependency missing | Use an already configured interpreter with jsonschema, or perform manual workflow. Help/request do not require it; nothing auto-installs. |
| Intel exit 3 / source Stale or Unavailable | At least one enabled source has no fresh data. Read `sourceStatus` for the error. Offline or no `--allow-network` means cache only; never treat old data as current. Retry later for rate limits or outages. |
| Intel cache refused | The cache path must not be a symlink (for example macOS `$TMPDIR` under `/var`) and its directory must be private (0700). Use the default `.panda-suite/blue/intelligence-cache` or a real private path. |
| No project exposure rows | Package queries need `--allow-package-queries`, and automatic inventory reads only npm `package-lock.json` v2/v3. For other ecosystems supply a reviewed `--components` file. No rows is not proof of no exposure. |
| Sensitive output | Use a private exact-value redactions file; inspect sanitized JSON/Markdown before sharing. Unknown secrets in arbitrary prose/paths need human review. Never validate tokens externally. |

Helper exits describe parsing/transformation/publication, not severity: 0 operation
completed, 2 refused/error, 3 an intel source
that is not fresh. Windows remains unverified; trusted local root assumptions are not a sandbox.
