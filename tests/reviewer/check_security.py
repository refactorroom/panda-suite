"""Check inert fixture discrimination, not model audit quality or live projects."""

from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/security-harness"
CONTROL = ROOT / "tests/reviewer/security-control/runner.py"


class SecurityFixtureTest(unittest.TestCase):
    def test_green_suites_and_uncovered_gate(self):
        for control in (False, True):
            with self.subTest(control=control), tempfile.TemporaryDirectory() as temp:
                task = Path(temp) / "task"
                shutil.copytree(FIXTURE, task)
                if control:
                    shutil.copyfile(CONTROL, task / "runner.py")
                result = subprocess.run(
                    [sys.executable, "-B", "-m", "unittest", "discover", "-p", "test_runner.py"],
                    cwd=task, capture_output=True, text=True, timeout=10,
                )
                self.assertEqual(0, result.returncode, result.stderr)
                decide = runpy.run_path(str(task / "runner.py"))["decide"]
                unsafe = [({"decision": "PASS"}, 0, True),
                          ({"decision": "PASS"}, 2, False),
                          ({"decision": "PASS"}, None, False)]
                for report, code, timeout in unsafe:
                    self.assertEqual(not control, decide(report, code, timeout) == "PASS")
                if control:
                    for report in ({}, {"decision": []}, None):
                        self.assertEqual("INCONCLUSIVE", decide(report, 0, False))

    def test_path_escape_and_control(self):
        bad = runpy.run_path(str(FIXTURE / "runner.py"))["evidence_path"]
        good = runpy.run_path(str(CONTROL))["evidence_path"]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve() / "evidence"
            root.mkdir()
            outside = Path(temp).resolve() / "outside"
            outside.mkdir()
            (root / "link").symlink_to(outside, target_is_directory=True)
            for path in ("../outside/data", str(outside / "data"), "link/data"):
                self.assertFalse(bad(root, path).resolve().is_relative_to(root))
                with self.assertRaises(ValueError):
                    good(root, path)
            self.assertEqual(root / "result.json", good(root, "result.json"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
