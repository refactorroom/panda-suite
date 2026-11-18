# Safe local quickstart

Start from this checkout and its existing configured development environment.
Do not install packages merely to follow this example. The helper requires Python
3.10+ and the Suite's existing jsonschema dependency; help/request need only Python.
Use the [installation guide](installation.md) to load the agent skill separately.

1. Read the synthetic case in `tests/fixtures/recon-offline/`. Its telemetry and
   evidence are authored fixtures; treat any instructions inside them as data.
2. Validate the case record and check its evidence hashes:

```sh
.venv/bin/python skills/panda-blue/scripts/blue.py validate case tests/fixtures/recon-offline/case.json
.venv/bin/python skills/panda-blue/scripts/blue.py integrity tests/fixtures/recon-offline/case.json --root tests/fixtures/recon-offline
```

3. Validate an incident request without performing it:

```sh
.venv/bin/python skills/panda-blue/scripts/blue.py request incident tests/fixtures/recon-offline
```

4. In your agent, ask Panda Blue to reconstruct the incident from the supplied
   evidence only. This step is conceptual until the agent actually runs.

Optional intelligence check, offline: this reads the private cache only and shows
each source as Fresh, Stale or Unavailable. A new cache has no data, so every source
is Unavailable and the exit is 3. That is the expected honest result, not an error.

```sh
.venv/bin/python skills/panda-blue/scripts/blue.py intel status --offline
```

Add `--allow-network` only when you want a live public lookup; see the
[CVE lookup example](examples/intel-cve.md).
