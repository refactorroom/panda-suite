"""Report format and blind preparation checks; no behavioral model claims."""

import copy
import json
from pathlib import Path
import runpy
import tempfile
import unittest

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "skills/panda-security/assets"
prepare = runpy.run_path(str(ROOT / "scripts/prepare-evaluation.py"))["prepare"]
install = runpy.run_path(str(ROOT / "scripts/install-skills.py"))["install"]


class SecurityContractTest(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads((ASSETS / "findings.schema.json").read_text())
        self.example = json.loads((ASSETS / "findings.example.json").read_text())
        self.validator = jsonschema.Draft202012Validator(self.schema)

    def test_example_and_unknown_metadata(self):
        jsonschema.Draft202012Validator.check_schema(self.schema)
        self.validator.validate(self.example)
        self.assertIsNone(self.example["audit"]["revision"])
        self.assertIsNone(self.example["scans"][0]["exitCode"])

    def test_incomplete_or_malformed_findings_rejected(self):
        for field in ("evidence", "impact", "controlsConsidered", "regression", "verification"):
            report = copy.deepcopy(self.example)
            del report["findings"][0][field]
            with self.subTest(field=field), self.assertRaises(jsonschema.ValidationError):
                self.validator.validate(report)
        for field, value in (("severity", "CVSS 10"), ("confidence", "secure"),
                             ("cwe", "CVE-invented"), ("evidence", [])):
            report = copy.deepcopy(self.example)
            report["findings"][0][field] = value
            with self.subTest(field=field), self.assertRaises(jsonschema.ValidationError):
                self.validator.validate(report)

    def test_report_version_and_explicit_coverage_required(self):
        for field, value in (("schemaVersion", "latest"), ("coverage", None), ("scans", {})):
            report = copy.deepcopy(self.example)
            report[field] = value
            with self.subTest(field=field), self.assertRaises(jsonschema.ValidationError):
                self.validator.validate(report)
        report = copy.deepcopy(self.example)
        report["findings"] = []
        report["coverage"][0]["status"] = "Unverified"
        self.validator.validate(report)  # Empty findings do not imply inspected coverage.

    def test_new_scenarios_prepare_blind_in_each_arm(self):
        cases = json.loads((ROOT / "tests/scenarios/cases.json").read_text())
        cases = [c for c in cases if c["id"].startswith("SECURITY-")]
        self.assertGreaterEqual(len(cases), 10)
        fixture = ROOT / "tests/fixtures/security-harness"
        sources = {p.relative_to(fixture): p.read_bytes() for p in fixture.rglob("*")
                   if p.is_file() and "__pycache__" not in p.parts}
        with tempfile.TemporaryDirectory() as temp:
            for case in cases:
                for arm in ("baseline", "specialist", "lead"):
                    dest = Path(temp) / (case["id"] + arm)
                    prepare(ROOT, dest, case["id"], arm)
                    actual = {p.relative_to(dest): p.read_bytes() for p in dest.rglob("*")
                              if p.is_file() and p.name != "TASK.txt"}
                    self.assertEqual(sources, actual)
                    prompt = (dest / "TASK.txt").read_text()
                    self.assertTrue(prompt.endswith(case["prompt"] + "\n"))
                    for check in case["checks"]:
                        self.assertNotIn(check, prompt)

    def test_rename_is_a_single_standalone_skill(self):
        self.assertFalse((ROOT / "skills/panda-sec").exists())
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "skills"
            self.assertEqual(["panda-security"], install(ROOT, dest, ["panda-security"]))
            self.assertTrue((dest / "panda-security/assets/findings.schema.json").is_file())
            with self.assertRaises(ValueError):
                install(ROOT, dest, ["panda-sec"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
