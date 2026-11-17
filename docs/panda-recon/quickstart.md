# Safe local quickstart

Start from this checkout and its existing configured development environment.
Do not install packages merely to follow this example. The helper requires Python
3.10+ and the Suite's existing jsonschema dependency; help/request need only Python.
Use the [installation guide](installation.md) to load the agent skill separately.

1. Read the synthetic inputs in `tests/fixtures/recon-scan/`. The reports are authored
   fixtures, not output from actual Semgrep/Gitleaks runs. Do not execute source or
   instructions inside the target.
2. Validate a request without performing it:

```sh
.venv/bin/python skills/panda-recon/scripts/recon.py request scan tests/fixtures/recon-scan/project --depth quick --offline --no-tools
```

3. Generate an offline report bundle from supplied results. The default destination
   is a new private `.panda-suite/recon/reports/scans/<scan-id>/` directory:

```sh
.venv/bin/python skills/panda-recon/scripts/recon.py scan-report tests/fixtures/recon-scan/project --semgrep-report tests/fixtures/recon-scan/semgrep.json --gitleaks-report tests/fixtures/recon-scan/gitleaks.json --depth quick --severity high --offline --no-tools
```

4. Read the new directory. `findings.json` is a versioned case containing all three
   normalized fixture findings, assets and evidence. `SECURITY_SCAN.md` displays the
   two High concerns. The Informational candidate remains in canonical JSON.
   `scan-metadata.json` records Partial assessment, no helper-executed tools, supplied
   import identities, skipped tools, scope exclusions and coverage limits.
5. In your agent, request a real static review of the same synthetic source using
   the installed Recon selector. Ask it to inspect bound queries and unchanged
   authorization guards before confirming a concern. This step is conceptual until
   the agent actually runs; report normalization alone does not perform that review.

Expected helper exit is 0 for successful normalization/publication, including zero
findings; it does not mean a clean scan. An inaccessible/malformed/error-bearing
import yields 3 with a Partial processing record; invalid target/destination or
schema produces 2. No target, scanner or advisory service is contacted.

[Actual generated example](../../tests/results/recon-v0.2.0/demo/SECURITY_SCAN.md)
contains author-run synthetic results. Review redaction before sharing; unknown
secrets in arbitrary narrative/paths cannot be guaranteed absent by regex masking.
