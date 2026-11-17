# Security rebrand validation — 2026-11-17

Source change only; no publication, global installation, security scan or production
operation. All commands below ran from the Panda Suite repository unless noted.

| Check | Actual result |
| --- | --- |
| `.venv/bin/python scripts/validate-skills.py` | Passed: 27 skills, metadata, standalone references, manifests and scenario coverage. |
| `.venv/bin/python -B -m unittest discover -s tests -p test_security.py -v` | Five passed: schema/example and invalid shapes, unknown metadata, blind preparation in 33 case/arm combinations, standalone renamed skill and rejected old name. |
| `.venv/bin/python -B tests/reviewer/check_security.py` | Two passed: both ordinary three-test suites green; independent probes distinguish defective gate/path behavior from correct control. No provider or network execution. |
| `.venv/bin/python -B -m unittest discover -s tests -p test_tooling.py -v` | Thirty-two passed, including independent installation, scenario boundaries, metadata mutations and pinned upstream integrity. |
| `.venv/bin/python scripts/build-docs.py` | Built 52 pages including 27 skill guides. |
| `.venv/bin/python scripts/check-docs.py` | 52 pages and 3,401 internal links passed. |
| `python3 tests/check_codex_discovery.py` | Codex CLI 0.159.2 discovered 27 portable-plugin and temporary standalone skills including panda-security, without panda-sec. No installation/model run. The returned installed flag describes existing app state, not an action performed here. |
| `claude plugin validate .claude-plugin/plugin.json` | Passed. |
| `claude --plugin-dir /absolute/path/to/panda-suite plugin details panda-suite` | 27 skills including panda-security, zero agents/hooks/MCP servers. Inventory only; no interactive model run. |
| `node --test tests/npm-cli.test.js` | Four passed, five failed under Node v26.10.0. Same five failures reproduced on pristine committed HEAD; see linked evidence below. |
| `git diff --check` | Passed for tracked changes; additional whitespace check covered new text files. |

The reviewer path probe initially failed on macOS `/var` versus `/private/var`
alias comparison; canonicalizing the temporary root corrected the reviewer test.
This was a test-path issue, not an observed skill or real-harness security failure.

The npm failures occur in unchanged installer tests. A focused synthetic install
returned `Target already exists: cp returned EEXIST` during directory copying.
An isolated `git archive HEAD` checkout reproduced the same four-pass/five-fail
suite under the same Node runtime. [Pristine-HEAD record](npm-head-check.json)
retains revision, runtime, exit and summary. Installer code/tests were preserved;
this authoring change does not resolve that pre-existing compatibility issue.

[Source review identities](source-review.json) retain inspected local project
revisions and file hashes. Installed Evaris reports v0.2.0; Invaris --version
returned unsupported action, exit 2; Itervyn was absent on PATH. No real cross-tool
execution, scanner adapter or updated integration compatibility is established.

## Behavioral comparison

| Arm | Status | Actual model answer/action evidence |
| --- | --- | --- |
| Ordinary baseline | Not Run | None |
| Frozen original panda-sec | Not Run | None; instructions preserved under original/ |
| Revised panda-security | Not Run | None; runnable blind cases prepared and checked only |

No fresh model tasks were launched. Evaris prepares/imports/evaluates externally
obtained results; its presence does not establish an agent run. No model-quality,
injection-resistance, audit-accuracy, elapsed-time or token-saving conclusion is
supported. Claude inventory token figures are host estimates, not measured task
consumption. Synthetic probes establish case validity, not model effectiveness.

Next justified work: fresh comparable application, harness, injection, saved-report
and nonactivation trials, with actual actions and reports graded independently.
Manual report redaction/deduplication, scanner behavior and production security
remain outside deterministic schema/fixture validation.
