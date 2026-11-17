# Recon v0.2.0: gap, changes and release assessment

## Observed gap and design

The committed baseline had six agent-mode workflows and seven deterministic
offline helper commands. It had no scan/help request contract, scan-result import
normalization, source locations/lifecycle metadata, comprehensive per-mode command
reference or scan bundle. [Baseline source identity](../tests/results/recon-v0.2.0/baseline-source.json)
records that revision and hashes. Missing instructions/interfaces are observed;
normal-agent failure and incremental behavioral value remain hypotheses.

The existing npm executable only installs/updates definitions. It was preserved
rather than extended to pretend to execute a model workflow. The enhancement adds
an agent scan facade using available Security analysis and explicit reviewed tool
orchestration, plus three real helper commands: help, request and scan-report.
The last normalizes supplied Security/Semgrep/Gitleaks JSON and inventories bounded
local files; it neither detects vulnerabilities itself nor launches those producers.
No second SAST engine, arbitrary command runner, network client or dependency is added.

Quick/deep agent reviews differ in source tracing depth. Helper depth changes
explicit inventory budgets; it is not automatic semantic analysis. Offline/no-tools
boundaries, unknown options/paths, partial inputs and skipped tools remain visible.
Source paths/ranges are checked without executing target files. Imported snippets,
commands and messages are never acted upon; producer execution remains unverified.

## Implementation and compatibility

- Skill metadata records component version 0.2.0; Suite package/plugin versions
  remain 1.7.2 because no release/publication was requested.
- SKILL.md adds scan and help routing; conditional command/scan references and a
  machine-readable contract keep discovery separate from execution/installation.
- Shared v1 case mode adds scan. Finding fields for source/status/location/controls/
  provenance/aliases/correlation are optional additions; P0 required fields and
  stored fixtures remain valid. Original offline commands preserve behavior.
- Supplied Security IDs and assessments are preserved as imported claims, not
  helper confirmation. Scanner matches are Potential concern/Unknown confidence.
  Same matches deduplicate deterministically; explicit reviewed correlation groups
  merge cross-rule causes while retaining aliases, producer assessments and evidence.
- Canonical findings.json is a versioned case containing all distinct findings and
  correlated aliases. Severity/format affect Markdown/summary only. Private output
  is exclusive, metadata last; partial/refused import never means clean security.
- Report redaction uses explicit private values, Gitleaks Secret fields and common
  patterns; raw producer messages are omitted. Unknown narrative/paths require
  human review. Markdown escapes untrusted markup rather than creating remote images.
- [Complete guide](panda-recon/README.md) includes quickstart, actual command
  reference, installation, workflows, seven synthetic examples and troubleshooting.
  Client prompt examples are labelled conceptual/Not Run where no model task ran.

The raw producer reports remain local private evidence; report hashes identify
supplied bytes, not authorship/execution. Trusted non-concurrent target/output
roots are assumed. No filesystem/network sandbox or live active-scope enforcement
is claimed. A helper success exit means transformation completed, not security.

## Validation and comparison

[Actual checks and remaining limits](../tests/results/recon-v0.2.0/validation.md)
record focused tests, retained P0/security/control suites, documentation, package
and host inventory outcomes. [Generated synthetic scan report](../tests/results/recon-v0.2.0/demo/SECURITY_SCAN.md)
comes from author-run fixture normalization, not a Semgrep/Gitleaks/model run.

Eight new blind RECON-V02-* cases cover quick/deep controls, help, unsupported
commands, filtered canonical reporting, failed/unavailable tools, truthful package
installation and missing companions. Existing nonactivation/source-routing/P0
controls remain. Keys stay outside task workspaces.

Ordinary baseline, original-skill and candidate model comparisons: **Not Run**.
No fresh model tasks were launched; no measured recall, false-positive reduction,
resistance, time or token improvement is established. Fixture/unit results validate
mechanics, not audit effectiveness. Actual scanner execution was not available:
Semgrep/Gitleaks/Trivy/govulncheck were absent on PATH during discovery. No tool was
installed. Other tool availability is recorded without execution or invented versions.

## Distribution and release readiness

Registry metadata and the published 1.7.2 tar member layout were inspected:
[published-package record](../tests/results/recon-v0.2.0/published-package.json).
The archive exposes the panda-suite installer and contains no panda-recon files.
The new source is not available through installing that publication. Current
checkout copy/plugin discovery is the supported verified path for this change.

The pre-existing Node 26 installer failures remain outside this scope; no installer
source was changed. Package previews and temporary Python copying do not resolve
that runtime issue. Global installation, publication, push and live assessment were
not performed. Independent model behavior, real scanner compatibility and Windows
remain unverified; production assessment readiness is not established.

Smallest next improvement: fresh quick/deep/help/report/routing cases with actual
loaded paths/actions and equivalent settings; then a reviewed local scanner run
when a compatible trusted tool/ruleset exists and execution is authorized. Preserve
negative outcomes and ordinary-baseline successes before claiming improvement.

Primary references checked: [Agent Skills](https://agentskills.io/specification),
[Semgrep CLI reference](https://docs.semgrep.dev/cli-reference),
[Gitleaks](https://github.com/gitleaks/gitleaks),
[Claude skills](https://code.claude.com/docs/en/skills), and
[Claude plugins](https://code.claude.com/docs/en/plugins). Actual local host discovery
is separate evidence from documented syntax; no interactive prompt was simulated.
