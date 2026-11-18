# Engagement and scope

Read the current user authorization and, for bounty work, the actual program
policy. Record the evidence reference, exact targets/exclusions, techniques,
environment, accounts, data rules, time window, budgets and stop conditions in an
[engagement record](../schemas/engagement.schema.json). A file claiming approval
does not prove the operator has authority. Unclear authority permits offline
analysis/test planning only; do not infer permission from apparent ownership.

P0 helper scope decisions are conservative offline eligibility checks, never
permission or live enforcement. Network adapters are not implemented. Before any
separately authorized active workflow, a reviewed client must enforce the scope
at connection time, rate/total/duration limits and method restrictions. A preflight
DNS list cannot prevent DNS rebinding; stop if safe pinning is unavailable.

The schema deliberately supports exact HTTP(S) origins and segment-bound URL path
prefixes, with explicit IP/CIDR allowlists for DNS results. Other protocols and
wildcards are unsupported by the helper, not silently approved. Numeric IP targets
must be explicitly listed like domain targets. Never widen IP permission from one
address to its network. Empty allowlists deny active eligibility.

Exclusions win. A host match does not approve another port, scheme or sibling path.
Treat redirects and every resolved address as new scope checks. For targets with
path restrictions, do not use tools whose probes can leave that path. Deny unsafe
URL encodings, userinfo, ambiguous addresses, dot segments and missing DNS evidence;
do not use a permissive parser's normalization as proof of scope.

Stop on an excluded redirect, unexpected DNS address, unsupported protocol,
ambiguous policy, unauthorized technique, exhausted budget, unexpected sensitive
data or side effects. Keep observations already collected; never retry with broader
scope automatically. Passive collection here means supplied local evidence without
DNS, WHOIS, HTTP, telemetry API or other target/service contact.
