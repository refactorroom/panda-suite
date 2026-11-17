# Look up current intelligence for one CVE

## Scenario

Check whether a known CVE is in CISA KEV, what its current EPSS score is, and
whether the project's npm dependencies are affected.

## Prerequisites and input

Use the current checkout and a host that discovers the skill. Live lookup needs
network permission. Sending package names and versions to OSV needs a separate
permission. Without either, the helper reads only the dated local cache. The
deterministic tests use the mocked responses in `tests/fixtures/recon-intelligence/`.

## Invocation

Conceptual standalone Codex prompt; interactive execution is **Not Run**. For Claude/plugin names use the installation guide.

```text
$panda-recon intel cve CVE-2021-44228
Use live public sources. Do not send source code or private paths. Show source dates and freshness.
```

The corresponding verified request parser validates input only:

```sh
.venv/bin/python skills/panda-recon/scripts/recon.py request intel cve CVE-2021-44228
```

The helper performs the lookup only when network use is explicit:

```sh
.venv/bin/python skills/panda-recon/scripts/recon.py intel cve CVE-2021-44228 --allow-network --output .panda-suite/recon/reports/intel-example
```

## What the agent does

Retrieve the NVD record, KEV membership and the dated EPSS score. Keep CVSS, KEV
and EPSS as separate signals. Leave missing fields null. Correlate with local
components only when an inventory and package-query permission exist.

## Expected result structure

CVE_ANALYSIS.md, intelligence.json and source-status.json; PROJECT_EXPOSURE.md
only when a local component matches. Each claim keeps its source URL, publication
or modification date and retrieval time.

## Illustrative Markdown excerpt

> KEV: listed by CISA (catalog date shown in sources). EPSS: probability estimate
> dated in the record, not evidence of an attack. Project exposure: not assessed
> because no component inventory was supplied.

This excerpt is an authored expectation, not a successful execution log or a measured agent answer.

## Important limitations

KEV membership does not mean this project was compromised. A stale or unavailable
source is reported as such (helper exit 3). No scheduler or monitoring is active.
