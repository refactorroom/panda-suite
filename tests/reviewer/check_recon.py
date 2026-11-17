"""Validate synthetic positive/negative controls; no model or live-system claim."""

from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/fixtures/recon-offline'
CONTROL = ROOT / 'tests/reviewer/recon-control/object_api.py'


class ReconControlTest(unittest.TestCase):
    def test_green_ordinary_suites_leave_cross_account_gap(self):
        for corrected in (False, True):
            with self.subTest(corrected=corrected), tempfile.TemporaryDirectory() as temp:
                task = Path(temp) / 'task'
                shutil.copytree(FIXTURE, task)
                if corrected:
                    shutil.copyfile(CONTROL, task / 'object_api.py')
                result = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-p', 'test_objects.py'],
                                        cwd=task, text=True, capture_output=True, timeout=10)
                self.assertEqual(0, result.returncode, result.stderr)
                read = runpy.run_path(str(task / 'object_api.py'))['read_object']
                row = {'owner': 'synthetic-alice', 'value': 'synthetic-document'}
                self.assertEqual(row, read('synthetic-alice', 'doc1', {'doc1': row}))
                self.assertEqual(corrected, read('synthetic-bob', 'doc1', {'doc1': row}) is None)


if __name__ == '__main__':
    unittest.main(verbosity=2)
