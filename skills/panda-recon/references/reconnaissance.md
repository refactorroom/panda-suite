# Offline reconnaissance

Inventory the supplied repository/configuration/network export only within the
requested roots. Capture applications, modules, APIs, workers, authentication
boundaries, sensitive operations and external integrations supported by evidence.
For each asset record an ID, locator/type, source evidence, observation time,
scope classification, exposure claim and confidence. Use the
[asset schema](../schemas/asset.schema.json).

A hostname in source is a configured reference, not observed external reachability
or permission to resolve/contact it. Supplied DNS/network inventories may be stale;
record their timestamps and preserve conflicting addresses or ownership evidence.
Distinguish declared endpoints, local listeners, externally observed services and
unverified exposure. Related domains, redirects, cloud/CDN addresses and third-party
services remain outside scope unless explicitly authorized.

Develop one testable hypothesis per material boundary with the evidence needed to
decide it. Prioritize exposed and privileged operations; do not inflate asset count
with duplicate aliases or label every endpoint vulnerable. Pass source-only audit
questions to Security when deeper analysis is needed, with the exact evidence/scope.

Use ATTACK_SURFACE.md for assets/boundaries/unknowns; RECON_REPORT.md for the
assessment answer and next permitted checks. asset-inventory.json preserves the
normalized asset records. The P0 `inventory` helper only reconciles a supplied
structured inventory with declared scope; it does not crawl or scan a repository.
