# Invaris integration

Evaris 0.4.0 documents two actions: `check`, with a restricted
`invaris.dev/v1alpha2` harness and `invaris.evidence/v1alpha2` evidence, and
`campaign`, with an `invaris.campaign/v1alpha1` file whose harnesses are
listed in `files`. Earlier Evaris versions support `check` only. Challenges
and mutations reach Evaris only through a campaign. Report native
verification and Evaris assessment separately: required REJECT fails;
required REFUSE, ERROR or UNAVAILABLE is inconclusive; ACCEPT cannot
override failed or missing task criteria.
