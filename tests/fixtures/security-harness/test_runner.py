import unittest
from pathlib import Path

from runner import decide, evidence_path


class RunnerTest(unittest.TestCase):
    def test_successful_provider(self):
        self.assertEqual("PASS", decide({"decision": "PASS"}, 0, False))

    def test_rejected_provider(self):
        self.assertEqual("FAIL", decide({"decision": "FAIL"}, 1, False))

    def test_evidence_location(self):
        root = Path("evidence").resolve()
        self.assertEqual(root / "result.json", evidence_path(root, "result.json"))
