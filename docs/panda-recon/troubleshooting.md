# Troubleshooting

| Symptom | Check and correction |
| --- | --- |
| Skill absent | Confirm the selected host directory/plugin inventory, complete copied references and supported metadata. Refresh host; avoid duplicate copies. Discovery is not model execution. |
| `scan` unknown in a shell | `$panda-recon scan ...` is an agent prompt. Use `recon.py request` for grammar validation or `scan-report` for local report normalization; npm CLI only installs/updates. |
| Unknown mode/option or missing argument | Run helper `help` / `help MODE` or `--help`. Use the seven mode names; scan options are not accepted for unrelated helper commands. |
| Invalid target | Use an existing authorized repository directory for scan; no linked roots or parent-scope fallback. Other agent modes need their appropriate evidence/policy path. |
| Unsupported report/format | Supply documented Security v1, Semgrep results/errors or Gitleaks JSON array. Markdown/SARIF/binary reports are not parser inputs. Agent analysis can use other accessible evidence with explicit limits. |
| Scanner unavailable | Record Missing/Not Run and continue static work; do not install or fabricate results. PATH availability alone proves neither version nor safe execution. |
| Permission denied | Respect the denied root/output; choose an authorized accessible destination. Do not elevate privileges or broaden scope automatically. |
| Empty findings | Inspect assessmentStatus, coverage, imports, caps and tools. Empty canonical findings after no/failed imports is Partial, never proof of security. |
| Partial scan/import | Preserve error/refusal, raw private evidence and valid other inputs. Resolve tool/configuration/source-version gaps; re-run at a new destination. |
| Producer timeout/nonzero | Preserve actual producer status/output limits. Semgrep error-bearing imports are refused; imported execution is not independently verified. A failed tool cannot establish a fix or clean result. |
| Missing case evidence | Keep Not tested/Inconclusive. Restore authorized original bytes or identify collection gaps; never change a hash to manufacture a match. |
| No active authorization | Stay offline. A manifest/discovered host is not authority; establish exact assets/techniques/budgets before permitted testing. |
| Existing output/report failure | Old scans are never overwritten. Choose a fresh directory; missing metadata means incomplete publication. Keep failure evidence rather than relabeling it complete. |
| Helper dependency missing | Use an already configured interpreter with jsonschema, or perform manual workflow. Help/request do not require it; nothing auto-installs. |
| Sensitive output | Use a private exact-value redactions file; inspect sanitized JSON/Markdown before sharing. Unknown secrets in arbitrary prose/paths need human review. Never validate tokens externally. |

Helper exits describe parsing/transformation/publication, not severity: 0 operation
completed, 2 refused/error, 3 partial scan-report processing. Agent scan statuses
and producer-specific exits are separate. Windows and active scanner execution
remain unverified; trusted local root assumptions are not a sandbox.
