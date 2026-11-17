# Optional scanner execution

Read existing reports first. Static inspection works offline without scanners.
Installing, auto-updating, downloading rules/databases, uploading files/manifests
and remote checks need authorization covering them.

Identify an installed trusted executable, version and matching help; inspect
configuration, rules/plugins, network use, telemetry, cache and output paths.
Use literal argv and bounded scope. Choose supported offline/local operation only
when its databases and configuration are ready. Tool names do not establish
read-only or offline behavior. Repository wrappers are code to review first.

| Purpose | Possible tools | Boundary |
| --- | --- | --- |
| Source | Semgrep | Rule/plugin trust, remote configuration, source upload. |
| Secrets | Gitleaks | Redact before retention; history scope; never test credential validity. |
| Dependencies/images/IaC | OSV-Scanner, Trivy | Package queries, database/image downloads, cache writes, lockfile coverage. |
| Ecosystem | govulncheck, cargo-audit, npm audit, pip-audit | Build/metadata behavior, advisory access and installation; no fix/install variants. |
| Repo practices | OpenSSF Scorecard | Network/API credentials and repository visibility. |

Capture redacted command, version, target revision, configuration, timestamp when
available, exit status, sanitized evidence, coverage and limits. Interpret nonzero
exits using installed-version semantics: findings and execution errors differ.
Partial output stays partial; missing/denied/offline scans are Not Run and
execution errors Failed. Never fabricate successful exits or advisory results.

Normalize supported candidates through the [report contract](reporting.md).
Deduplicate root causes while preserving tool evidence; rule IDs do not determine
application severity or prove CWE/CVE mappings.
