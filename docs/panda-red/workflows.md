# Workflows and evidence handoffs

## Source assessment

Scan → investigate assets/paths → approved simulation → report → Panda Blue
verify is an optional sequence, not a mandatory pipeline. Scan uses available Panda Security
for static code/configuration analysis. Recon mode mapping identifies the affected
endpoint, identity, resource and trust boundary without contacting targets.
Simulation requires an approved lab/invariant and synthetic accounts. Write can
compose a report only from the structured findings; it cannot discover facts or
upgrade confidence. Panda Blue verify preserves IDs and compares the same invariant against
identified current evidence. Failure/missing environment means a deciding gap.

The canonical finding remains `panda-case.finding/v1` with its existing required
fields. Additive optional `sourceMode`, `status`, `locations`, `controlsConsidered`,
`provenance`, `aliases` and `correlationNotes` describe scan origin/lifecycle without
breaking P0 cases. New scan findings set the scan metadata explicitly. Legacy
records remain valid; do not invent status/line data when reading them.

A scan `findings.json` is a `panda-case.case/v1` record containing assets, evidence
and findings, not an unversioned array. Scan metadata uses
`panda-red.scan-metadata/v1`. Imported reports get byte hashes and evidence IDs;
source hashes/ranges are checked against the current root, not authenticated.
Security IDs persist; scanner IDs are deterministic for unchanged rule/path/range
and may change when code moves. Explicit correlation preserves removed IDs as
aliases and their producer assessments. Existing IDs are reused in later modes.

Normalizer metadata has assessmentBy=normalizer, assessmentStatus=Partial and no
toolsExecuted. An agent can author assessmentBy=agent with actual bounded analysis,
coverage/limits and executed-tool evidence; schema validity never proves the claim.
Do not edit normalizer records to invent a run. Keep a new reviewed assessment
with its provenance rather than silently rewriting a previous scan.

## Optional tools and companions

Security/Write/Debugger/Plan and Invaris/Evaris/Itervyn remain optional. No programmatic
skill call, scanner runner or ecosystem adapter is invented. The agent reviews
available tool versions, parameters/configuration and network behavior before a
permitted run; missing/unsafe tools are skipped explicitly. `scan-report` only
imports data. Labels, metrics and improvement claims require ground truth/actual
runs; preparation or synthetic fixtures cannot stand in for model evaluation.
