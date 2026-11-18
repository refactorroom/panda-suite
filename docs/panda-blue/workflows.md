# Workflows and evidence handoffs

## Telemetry investigation

Supplied security logs → hunt → incident analysis when supported → report.
Preserve original timestamps/zones, collection bounds and conflicting evidence.
A suspicious sequence can justify further investigation without confirming intent
or compromise. Missing alerts can reflect absent collection rather than detection
failure. Lab simulations remain Simulation only. Containment, isolation, revocation
and external notifications are recommendations until authorization covers them.

## Fix verification

Panda Red or Panda Security supplies the finding ID, original evidence, invariant
and negative/control pair. `verify` reruns that pair against the identified revised
subject and records Fixed, Still vulnerable, Partially remediated, Not reproducible,
Not tested or Inconclusive. A green suite or missing environment is never Fixed.

## Threat intelligence

`intel` → hunt/incident with `--intel cache|live` → report. Intelligence is
retrieved with source dates and a Fresh/Stale/Unavailable status, then matched
only against local components or case evidence. `intel` writes `PROJECT_EXPOSURE.md`
rows only for exact package/version matches; hunt and incident keep external
intelligence in a separate dated section. KEV, EPSS and published campaigns never
upgrade a finding's status or an incident classification by themselves. Records
use `panda-blue.intelligence/v1`; reports are written to a new private directory.

## Optional tools and companions

Security/Write/Debugger/Plan and Invaris/Evaris/Itervyn remain optional. No programmatic
skill call, scanner runner or ecosystem adapter is invented. The agent reviews
available tool versions, parameters/configuration and network behavior before a
permitted run; missing/unsafe tools are skipped explicitly.  Labels, metrics and improvement claims require ground truth/actual
runs; preparation or synthetic fixtures cannot stand in for model evaluation.
