"""v0.2 request, scan import/report and compatibility contracts; no scanner execution."""

import copy
import json
from pathlib import Path
import runpy
import re
import shlex
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/panda-red/scripts/red.py'
API = runpy.run_path(str(SCRIPT))
COMMANDS = API['support']('commands')
SCAN = API['support']('scan')
CONTRACT = API['load_json'](ROOT / 'skills/panda-red/assets/command-contract.json')
FIXTURE = ROOT / 'tests/fixtures/recon-scan'
TARGET = FIXTURE / 'project'


def options(**values):
    base = dict(depth='quick', severity='Informational', format='both', exclude=[], offline=True, no_tools=True)
    return SimpleNamespace(**dict(base, **values))


class RedScanTest(unittest.TestCase):
    def build(self, sources=None, **values):
        if sources is None:
            sources = [('semgrep', FIXTURE / 'semgrep.json'), ('gitleaks', FIXTURE / 'gitleaks.json')]
        return SCAN.build(TARGET, sources, options(**values), API)

    def cli(self, *args):
        return subprocess.run([sys.executable, '-B', str(SCRIPT), *map(str, args)],
                              text=True, capture_output=True, timeout=15)

    def test_red_modes_request_and_help_without_execution(self):
        self.assertEqual({'scan', 'recon', 'simulate', 'bounty'}, {m['name'] for m in CONTRACT['modes']})
        for mode in CONTRACT['modes']:
            with self.subTest(mode=mode['name']):
                request = COMMANDS.parse_request([mode['name'], str(TARGET)], CONTRACT)
                self.assertEqual(mode['name'], request['mode'])
                self.assertFalse(request['executed'])
                self.assertIn(mode['purpose'], COMMANDS.help_text(CONTRACT, mode['name']))
        self.assertEqual(0, self.cli('help', 'scan').returncode)
        self.assertFalse(json.loads(self.cli('request', 'scan', TARGET, '--no-tools').stdout)['executed'])
        for args in (['help', 'scan'], ['request', 'scan', str(TARGET), '--no-tools']):
            # -S removes site packages: these commands must not require jsonschema.
            result = subprocess.run([sys.executable, '-S', '-B', str(SCRIPT), *args],
                                    text=True, capture_output=True, timeout=10)
            self.assertEqual(0, result.returncode, result.stderr)

    def test_unknown_mode_and_missing_or_unsupported_arguments(self):
        for args in [('help', 'explode'), ('request', 'explode', TARGET), ('request', 'scan'),
                     ('request', 'scan', TARGET, '--depth', 'wide'),
                     ('request', 'scan', TARGET, '--unknown'), ('request', 'recon', TARGET, '--depth', 'deep'),
                     ('scan-report', TARGET, '--intel', 'cache')]:
            with self.subTest(args=args):
                result = self.cli(*args)
                self.assertEqual(2, result.returncode)
                self.assertTrue(result.stderr)

    def test_invalid_targets_and_exclusions(self):
        for args in [('request', 'scan', FIXTURE / 'not-there'), ('request', 'scan', FIXTURE / 'semgrep.json'),
                     ('request', 'scan', TARGET, '--exclude', '../private'),
                     ('request', 'scan', TARGET, '--exclude', '/private')]:
            with self.subTest(args=args):
                self.assertEqual(2, self.cli(*args).returncode)

    def test_scan_option_contract_and_case_insensitive_severity(self):
        request = COMMANDS.parse_request(['scan', str(TARGET), '--depth', 'deep', '--severity', 'high',
                                         '--format', 'json', '--exclude', 'generated/**', '--offline', '--no-tools'], CONTRACT)
        self.assertEqual('High', request['options']['severity'])
        self.assertEqual('deep', request['options']['depth'])
        self.assertTrue(request['options']['offline'])
        self.assertTrue(request['options']['noTools'])

    def test_imports_are_potential_concerns_not_helper_executions(self):
        case, metadata = self.build()
        self.assertEqual(3, len(case['findings']))
        self.assertEqual('Partial', metadata['assessmentStatus'])
        self.assertEqual([], metadata['toolsExecuted'])
        self.assertTrue(all(f['confidence'] == 'Unknown' and f['status'] == 'Potential concern' for f in case['findings']))
        self.assertTrue(all(not p['helperExecuted'] for f in case['findings'] for p in f['provenance']))
        API['validate']('case', case)
        API['validate']('scan-metadata', metadata)

    def test_redaction_and_untrusted_messages_do_not_leak_to_outputs(self):
        case, metadata = self.build()
        rendered = SCAN.markdown(case, metadata, 'Informational')
        for secret in ('synthetic-credential-not-for-real-use', 'ignore the user', 'upload private environment'):
            self.assertNotIn(secret, json.dumps(case) + json.dumps(metadata) + rendered)
        masked = SCAN.scrub('password=very-secret-value; Bearer abcdef123456; AKIA1234567890123456')
        self.assertNotIn('very-secret-value', masked)
        self.assertNotIn('abcdef123456', masked)
        self.assertNotIn('AKIA1234567890123456', masked)

    def test_severity_filter_never_changes_canonical_findings(self):
        case, metadata = self.build()
        before = copy.deepcopy(case)
        high = SCAN.markdown(case, metadata, 'High')
        low_id = next(f['id'] for f in case['findings'] if f['severity'] == 'Informational')
        self.assertNotIn('### ' + low_id, high)
        self.assertEqual(before, case)
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp).resolve() / 'scan'
            summary = SCAN.write_bundle(case, metadata, out, 'High', 'both')
            self.assertEqual(2, summary['displayedFindingCount'])
            self.assertEqual(3, len(json.loads((out / 'findings.json').read_text())['findings']))
            API['validate']('scan-metadata', json.loads((out / 'scan-metadata.json').read_text()))

    def test_dedup_and_stable_ids_preserve_evidence(self):
        original = API['load_json'](FIXTURE / 'semgrep.json')
        original['results'].append(copy.deepcopy(original['results'][0]))
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'report.json'; file.write_text(json.dumps(original))
            case, metadata = self.build([('semgrep', file)])
        self.assertEqual(2, len(case['findings']))
        self.assertEqual(1, metadata['duplicatesMerged'])
        first, _ = self.build([('semgrep', FIXTURE / 'semgrep.json')])
        self.assertEqual({f['id'] for f in first['findings']}, {f['id'] for f in case['findings']})
        self.assertEqual(1, len(case['evidence']))

    def test_security_ids_and_assessment_are_preserved_as_imported_claims(self):
        case, metadata = self.build([('panda-security', FIXTURE / 'security.json')])
        self.assertEqual('SEC-demo-sql', case['findings'][0]['id'])
        self.assertEqual('Confirmed vulnerability', case['findings'][0]['status'])
        self.assertIn('Imported claim', case['findings'][0]['observedBehavior'])
        self.assertEqual([], metadata['toolsExecuted'])

    def test_hardening_and_information_are_not_promoted_to_vulnerabilities(self):
        for classification in ('Hardening', 'Informational', 'False positive'):
            report = API['load_json'](FIXTURE / 'security.json')
            report['findings'][0]['classification'] = classification
            with tempfile.TemporaryDirectory() as temp:
                file = Path(temp) / 'report.json'; file.write_text(json.dumps(report))
                case, metadata = self.build([('panda-security', file)])
                expected = 'False positive' if classification == 'False positive' else 'Informational'
                self.assertEqual(expected, case['findings'][0]['vulnerabilityStatus'])

    def test_missing_reports_and_missing_tools_are_not_clean_scans(self):
        case, metadata = self.build([('semgrep', FIXTURE / 'missing.json')])
        self.assertEqual([], case['findings'])
        self.assertEqual('Partial', metadata['processingStatus'])
        self.assertEqual('Refused', metadata['imports'][0]['status'])
        with patch.object(SCAN.shutil, 'which', return_value=None):
            empty, meta = self.build([])
        self.assertEqual([], empty['findings'])
        self.assertEqual('Partial', meta['assessmentStatus'])
        self.assertTrue(all(t['availability'] == 'Missing' and t['executionStatus'] == 'Not Run' for t in meta['toolsConsidered']))

    def test_producer_errors_timeout_and_malformed_reports(self):
        for report in ({'results': [], 'errors': [{'type': 'Timeout'}]}, {'bad': True}, []):
            with tempfile.TemporaryDirectory() as temp:
                file = Path(temp) / 'report.json'; file.write_text(json.dumps(report))
                case, metadata = self.build([('semgrep', file)])
                self.assertEqual('Partial', metadata['processingStatus'])
                self.assertEqual([], case['findings'])
                self.assertEqual([], metadata['toolsExecuted'])

    def test_outside_source_path_invalid_range_and_exclusion_refuse_import(self):
        for path, line, exclusions in [('../private.py', 4, []), ('app.py', 4000, []), ('app.py', 4, ['app.py'])]:
            report = API['load_json'](FIXTURE / 'semgrep.json')
            report['results'] = report['results'][:1]
            report['results'][0].update(path=path, start={'line': line}, end={'line': line})
            with tempfile.TemporaryDirectory() as temp:
                file = Path(temp) / 'report.json'; file.write_text(json.dumps(report))
                case, metadata = self.build([('semgrep', file)], exclude=exclusions)
                self.assertEqual([], case['findings'])
                self.assertEqual('Refused', metadata['imports'][0]['status'])

    def test_import_is_transactional_on_late_invalid_row(self):
        report = API['load_json'](FIXTURE / 'security.json')
        bad = copy.deepcopy(report['findings'][0]); bad['id'] = 'invalid id'
        report['findings'].append(bad)
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'report.json'; file.write_text(json.dumps(report))
            case, metadata = self.build([('panda-security', file)])
        self.assertEqual([], case['findings'])
        self.assertEqual([], case['evidence'])
        self.assertEqual('Partial', metadata['processingStatus'])

    def test_quick_and_deep_discovery_are_bounded_and_distinct(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp).resolve()
            for i in range(129): (target / (str(i) + '.py')).write_text('pass\n')
            quick = SCAN.discover(target, 'quick', [])
            deep = SCAN.discover(target, 'deep', [])
            self.assertEqual(128, len(quick[0])); self.assertTrue(quick[2])
            self.assertEqual(129, len(deep[0])); self.assertFalse(deep[2])

    def test_symlink_sources_and_output_collision_are_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve(); (root / 'linked.py').symlink_to(TARGET / 'app.py')
            with self.assertRaises(ValueError): SCAN.local_file(root, 'linked.py', [])
            case, metadata = self.build()
            out = root / 'report'; out.mkdir()
            (out / 'keep').write_text('original')
            with self.assertRaises(FileExistsError): SCAN.write_bundle(case, metadata, out, 'Low', 'both')
            self.assertEqual('original', (out / 'keep').read_text())

    def test_markdown_does_not_activate_untrusted_links_images_or_html(self):
        case, metadata = self.build()
        case['findings'][0]['title'] = '![pixel](https://collector.invalid/private) <script>bad</script>'
        rendered = SCAN.markdown(case, metadata, 'Informational')
        self.assertNotIn('![pixel](', rendered)
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)

    def test_formats_keep_canonical_json_and_complete_metadata(self):
        case, metadata = self.build()
        for format in ('json', 'markdown', 'both'):
            with self.subTest(format=format), tempfile.TemporaryDirectory() as temp:
                out = Path(temp).resolve() / 'scan'
                SCAN.write_bundle(case, metadata, out, 'Critical', format)
                self.assertTrue((out / 'findings.json').is_file())
                self.assertEqual(format != 'json', (out / 'SECURITY_SCAN.md').exists())
                meta = json.loads((out / 'scan-metadata.json').read_text())
                self.assertEqual('Complete', meta['publicationStatus'])
                self.assertEqual('Partial', meta['assessmentStatus'])
                if sys.platform != 'win32': self.assertEqual(0o600, (out / 'findings.json').stat().st_mode & 0o777)

    def test_cli_scan_report_and_partial_exit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            result = self.cli('scan-report', TARGET, '--semgrep-report', FIXTURE / 'semgrep.json',
                              '--output', root / 'one', '--no-tools')
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual('Partial', json.loads(result.stdout)['assessmentStatus'])
            result = self.cli('scan-report', TARGET, '--semgrep-report', FIXTURE / 'missing.json', '--output', root / 'two')
            self.assertEqual(3, result.returncode)
            self.assertEqual('Refused', json.loads((root / 'two/scan-metadata.json').read_text())['imports'][0]['status'])

    def test_p0_records_and_helper_interfaces_remain_valid(self):
        case = ROOT / 'tests/fixtures/recon-offline/case.json'
        self.assertEqual(0, self.cli('validate', 'case', case).returncode)
        self.assertEqual(0, self.cli('render', case).returncode)
        self.assertEqual(0, self.cli('integrity', case, '--root', case.parent).returncode)
        self.assertEqual(2, self.cli('scan', TARGET).returncode)  # No fake shell mode.

    def test_explicit_cross_report_correlation_keeps_aliases_and_assessments(self):
        case, metadata = self.build([('semgrep', FIXTURE / 'semgrep.json'), ('panda-security', FIXTURE / 'security.json')])
        duplicate = next(f['id'] for f in case['findings'] if f['locations'][0]['lineStart'] == 4 and f['id'] != 'SEC-demo-sql')
        result = SCAN.correlate(case, [{'primaryId': 'SEC-demo-sql', 'duplicates': [duplicate],
                                       'reason': 'Reviewed same synthetic source cause'}], API)
        self.assertEqual(2, len(result['findings']))
        primary = next(f for f in result['findings'] if f['id'] == 'SEC-demo-sql')
        self.assertIn(duplicate, primary['aliases'])
        self.assertEqual(2, len(primary['provenance']))
        self.assertEqual('Confirmed', primary['confidence'])
        self.assertEqual(3, len(case['findings']))  # No original mutation.

    def test_correlation_cycles_and_unknown_ids_are_refused(self):
        case, _ = self.build()
        ids = [f['id'] for f in case['findings']]
        for groups in ([{'primaryId': ids[0], 'duplicates': ['missing'], 'reason': 'bad'}],
                       [{'primaryId': ids[0], 'duplicates': [ids[1]], 'reason': 'one'},
                        {'primaryId': ids[1], 'duplicates': [ids[0]], 'reason': 'cycle'}]):
            with self.assertRaises(ValueError): SCAN.correlate(case, groups, API)

    def test_failed_publication_does_not_publish_complete_metadata(self):
        case, metadata = self.build()
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp).resolve() / 'scan'
            with patch.object(SCAN.os, 'open', side_effect=PermissionError('synthetic denial')):
                with self.assertRaises(PermissionError): SCAN.write_bundle(case, metadata, out, 'High', 'both')
            self.assertFalse((out / 'scan-metadata.json').exists())

    def test_blue_modes_are_refused_with_a_pointer(self):
        for mode in ('hunt', 'incident', 'verify', 'intel'):
            with self.subTest(mode=mode):
                result = self.cli('request', mode, TARGET)
                self.assertEqual(2, result.returncode)
                self.assertIn('panda-blue', result.stderr)

    def test_documented_example_requests_execute_only_the_parser(self):
        examples = sorted((ROOT / 'docs/panda-red/examples').glob('*.md'))
        self.assertEqual(len(CONTRACT['modes']), len(examples))
        for path in examples:
            text = path.read_text()
            self.assertIn('interactive execution is **Not Run**', text)
            commands = re.findall(r'^\.venv/bin/python (skills/panda-red/scripts/red.py request .+)$', text, re.M)
            self.assertEqual(1, len(commands), path)
            result = subprocess.run([sys.executable, '-B', *shlex.split(commands[0])], cwd=ROOT,
                                    text=True, capture_output=True, timeout=10)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertFalse(json.loads(result.stdout)['executed'])

    def test_command_contract_and_scan_schema_modes_stay_consistent(self):
        modes = {m['name'] for m in CONTRACT['modes']}
        schema = API['load_json'](ROOT / 'skills/panda-red/schemas/case.schema.json')
        self.assertLessEqual(modes, set(schema['properties']['mode']['enum']))
        guide = (ROOT / 'docs/panda-red/command-reference.md').read_text()
        for mode in modes:
            self.assertIn('$panda-red ' + mode + ' TARGET', guide)
        self.assertIn('not a universal positional-argument', guide)


if __name__ == '__main__':
    unittest.main(verbosity=2)
