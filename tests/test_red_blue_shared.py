"""panda-red and panda-blue stay standalone while sharing case records and core code."""

import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
RED = ROOT / 'skills/panda-red'
BLUE = ROOT / 'skills/panda-blue'
SHARED = ['scripts/case_core.py', 'schemas/asset.schema.json', 'schemas/case.schema.json',
          'schemas/evidence.schema.json', 'schemas/finding.schema.json', 'references/evidence.md']
CASE = ROOT / 'tests/fixtures/recon-offline/case.json'


def cli(skill, *args):
    script = ROOT / f'skills/panda-{skill}/scripts/{skill}.py'
    return subprocess.run([sys.executable, '-B', str(script), *map(str, args)],
                          text=True, capture_output=True, timeout=15)


class SharedTest(unittest.TestCase):
    def test_shared_files_are_byte_identical(self):
        for name in SHARED:
            with self.subTest(file=name):
                self.assertEqual((RED / name).read_bytes(), (BLUE / name).read_bytes(),
                                 'edit both copies of ' + name + ' together')

    def test_skills_do_not_reference_each_other_or_the_old_name(self):
        for skill, other in ((RED, 'panda-blue/'), (BLUE, 'panda-red/')):
            for path in skill.rglob('*'):
                if not path.is_file() or '__pycache__' in path.parts:
                    continue
                text = path.read_text()
                with self.subTest(file=str(path.relative_to(ROOT))):
                    self.assertNotIn('panda-recon', text)
                    self.assertNotIn(other, text)
                    self.assertNotIn('../panda-', text)

    def test_schema_ids_use_the_split_namespaces(self):
        expected = {'asset': 'panda-case', 'case': 'panda-case', 'evidence': 'panda-case',
                    'finding': 'panda-case', 'engagement': 'panda-red', 'scan-metadata': 'panda-red',
                    'intelligence': 'panda-blue'}
        for skill in (RED, BLUE):
            for path in (skill / 'schemas').glob('*.schema.json'):
                kind = path.name.removesuffix('.schema.json')
                schema = json.loads(path.read_text())
                with self.subTest(schema=str(path.relative_to(ROOT))):
                    self.assertEqual(f'urn:{expected[kind]}:{kind}:v1', schema['$id'])
                    text = path.read_text()
                    self.assertNotIn('urn:panda-recon', text)

    def test_red_case_validates_in_blue(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp).resolve() / 'scan'
            result = cli('red', 'scan-report', ROOT / 'tests/fixtures/recon-scan/project',
                         '--semgrep-report', ROOT / 'tests/fixtures/recon-scan/semgrep.json',
                         '--output', output, '--no-tools')
            self.assertEqual(0, result.returncode, result.stderr)
            findings = output / 'findings.json'
            self.assertEqual('panda-case.case/v1', json.loads(findings.read_text())['schemaVersion'])
            result = cli('blue', 'validate', 'case', findings)
            self.assertEqual(0, result.returncode, result.stderr)
        for skill in ('red', 'blue'):
            with self.subTest(skill=skill):
                self.assertEqual(0, cli(skill, 'validate', 'case', CASE).returncode)

    def test_old_recon_records_are_rejected(self):
        case = json.loads(CASE.read_text())
        case['schemaVersion'] = 'panda-recon.case/v1'
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'old-case.json'
            path.write_text(json.dumps(case))
            for skill in ('red', 'blue'):
                with self.subTest(skill=skill):
                    self.assertEqual(2, cli(skill, 'validate', 'case', path).returncode)

    def test_blue_has_no_route_to_active_work(self):
        api = runpy.run_path(str(BLUE / 'scripts/blue.py'))
        for name in ('scope_check', 'inventory', 'target_url'):
            self.assertNotIn(name, api)
        for action in ('scope', 'inventory', 'scan-report'):
            with self.subTest(action=action):
                self.assertEqual(2, cli('blue', action, CASE).returncode)
        red = runpy.run_path(str(RED / 'scripts/red.py'))
        self.assertIn('scope_check', red)
        self.assertNotIn('intel', red['main'].__code__.co_consts)

    def test_default_output_folders(self):
        self.assertIn(".panda-suite/red/reports/scans", (RED / 'scripts/red.py').read_text())
        self.assertIn(".panda-suite/blue/intelligence-cache", (BLUE / 'scripts/intel.py').read_text())


if __name__ == '__main__':
    unittest.main(verbosity=2)
