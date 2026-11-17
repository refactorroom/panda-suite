"""Mock-first intelligence, freshness, privacy and applicability checks. No live network."""

import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
from urllib.parse import parse_qs, urlsplit
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/panda-recon/scripts/recon.py'
API = runpy.run_path(str(SCRIPT))
INTEL = API['support']('intel')
NET = API['support']('intel_net')
SOURCES = API['support']('intel_sources')
STORE = API['support']('intel_store')
COMPONENTS = API['support']('components')
FIXTURE = ROOT / 'tests/fixtures/recon-intelligence'
NOW = '2026-11-17T09:00:00+00:00'


def fixture(name):
    return json.loads((FIXTURE / (name + '.json')).read_text())


class MockSources:
    def __init__(self):
        self.calls = []; self.fail = {}; self.responses = {}
        self.config = INTEL.configuration(API)

    def __call__(self, url, method, payload, timeout):
        source = next((s for s, row in self.config.items() if url.split('?', 1)[0] == row['endpoint']), None)
        if source is None: raise AssertionError('unexpected destination')
        self.calls.append((source, url, method, payload))
        if source in self.fail: raise NET.SourceError(self.fail[source])
        if source in self.responses: return self.responses[source]
        if source.startswith('owasp-'): return (FIXTURE / 'owasp.html').read_bytes(), 'text/html'
        if source == 'incidents': return (FIXTURE / 'incidents.xml').read_bytes(), 'application/rss+xml'
        return (FIXTURE / (source + '.json')).read_bytes(), 'application/json'


class IntelligenceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve(); self.mock = MockSources()

    def args(self, *values):
        return INTEL.parser().parse_args([*values, '--cache', str(self.root / 'cache')])

    def run_intel(self, *values, now=NOW):
        result = INTEL.run(self.args(*values), API, transport=self.mock, sleep=lambda _: None, now=now)
        API['validate']('intelligence', result)
        return result

    def paged_nvd(self, total, severities=None):
        """Serve `total` synthetic NVD records honoring startIndex/resultsPerPage, like the live API."""
        base = fixture('nvd')['vulnerabilities'][0]
        def serve(url, method, payload, timeout):
            if not url.startswith(self.mock.config['nvd']['endpoint']): return original(url, method, payload, timeout)
            self.mock.calls.append(('nvd', url, method, payload))
            query = parse_qs(urlsplit(url).query)
            start, size = int(query['startIndex'][0]), int(query['resultsPerPage'][0])
            rows = []
            for i in range(start, min(total, start + size)):
                row = copy.deepcopy(base); row['cve']['id'] = f'CVE-2099-{30000 + i}'
                row['cve']['configurations'] = [{'nodes': ['x' * 50]}]
                severity = (severities or {}).get(i, 'MEDIUM')
                row['cve']['metrics']['cvssMetricV31'][0]['cvssData'].update(baseSeverity=severity)
                rows.append(row)
            body = {'resultsPerPage': len(rows), 'startIndex': start, 'totalResults': total, 'version': '2.0', 'vulnerabilities': rows}
            return json.dumps(body).encode(), 'application/json'
        original = self.mock.__call__
        return serve

    def run_paged(self, *values, total, now=NOW, severities=None):
        result = INTEL.run(self.args(*values), API, transport=self.paged_nvd(total, severities), sleep=lambda _: None, now=now)
        API['validate']('intelligence', result)
        return result

    def test_nvd_real_volume_pages_fully_and_stores_compact_records(self):
        data = self.run_paged('update', '--source', 'nvd', '--allow-network', total=2500)
        status = next(s for s in data['sourceStatus'] if s['source'] == 'nvd')
        self.assertTrue(status['refreshSucceeded'], status)
        urls = [c[1] for c in self.mock.calls if c[0] == 'nvd']
        self.assertEqual(['1000', '1000', '1000'], [parse_qs(urlsplit(u).query)['resultsPerPage'][0] for u in urls])
        snapshot, _ = STORE.Store(self.root / 'cache').snapshot('nvd', {'sync': True})
        self.assertEqual(2500, len(snapshot['data']['records']))
        self.assertNotIn('configurations', snapshot['data']['records'][0])  # Window snapshots keep only used fields.

    def test_nvd_window_too_large_is_reported_not_truncated(self):
        data = self.run_paged('latest', '--allow-network', '--days', '30', total=40000)
        status = next(s for s in data['sourceStatus'] if s['source'] == 'nvd')
        self.assertEqual('NVD_WINDOW_TOO_LARGE', status['lastAttemptError'])
        self.assertEqual(1, len([c for c in self.mock.calls if c[0] == 'nvd']))  # Refused after the first page reports the total.

    def test_latest_defaults_to_one_day_and_incidents_to_seven(self):
        self.run_paged('latest', '--allow-network', total=1)
        query = parse_qs(urlsplit([c for c in self.mock.calls if c[0] == 'nvd'][-1][1]).query)
        start = datetime.fromisoformat(query['lastModStartDate'][0]); end = datetime.fromisoformat(query['lastModEndDate'][0])
        self.assertEqual(1, (end - start).days)
        self.assertEqual(7, INTEL.window_days(self.args('incidents')))
        self.assertEqual(3, INTEL.window_days(self.args('latest', '--days', '3')))

    def test_stuck_catch_up_can_be_restarted_explicitly_and_says_so(self):
        self.run_paged('update', '--source', 'nvd', '--allow-network', total=3)
        later = '2026-11-27T09:00:00+00:00'  # Ten days of missed runs: too many changes to catch up.
        stuck = self.run_paged('update', '--source', 'nvd', '--allow-network', total=40000, now=later)
        self.assertEqual('NVD_WINDOW_TOO_LARGE', next(s for s in stuck['sourceStatus'] if s['source'] == 'nvd')['lastAttemptError'])
        self.mock.calls.clear()
        restarted = self.run_paged('update', '--source', 'nvd', '--days', '1', '--allow-network', total=5, now=later)
        self.assertTrue(next(s for s in restarted['sourceStatus'] if s['source'] == 'nvd')['refreshSucceeded'])
        query = parse_qs(urlsplit(self.mock.calls[-1][1]).query)
        self.assertTrue(query['lastModStartDate'][0].startswith('2026-11-26T09:00'))
        self.assertTrue(any('not fetched' in v for v in restarted['limitations']))
        self.mock.calls.clear()
        self.run_paged('update', '--source', 'nvd', '--allow-network', total=0, now='2026-11-27T10:00:00+00:00')
        query = parse_qs(urlsplit(self.mock.calls[-1][1]).query)
        self.assertTrue(query['lastModStartDate'][0].startswith('2026-11-27T08:58'))  # Default resumes from the restart.

    def test_sync_merge_drops_records_outside_retention(self):
        self.run_paged('update', '--source', 'nvd', '--allow-network', total=3)
        later = '2026-11-25T09:00:00+00:00'  # Eight days later: the earlier records are outside the 7-day retention.
        self.run_paged('update', '--source', 'nvd', '--allow-network', total=0, now=later)
        snapshot, _ = STORE.Store(self.root / 'cache').snapshot('nvd', {'sync': True})
        self.assertEqual([], snapshot['data']['records'])

    def test_latest_ranks_kev_and_severity_and_report_shows_top_records(self):
        kev = fixture('kev'); kev['vulnerabilities'][0]['cveID'] = 'CVE-2099-30059'
        self.mock.responses['kev'] = (json.dumps(kev).encode(), 'application/json')
        original = self.paged_nvd(80, {5: 'CRITICAL', 7: 'HIGH'})
        def transport(url, method, payload, timeout):
            return original(url, method, payload, timeout) if 'nvd.nist.gov' in url else self.mock(url, method, payload, timeout)
        data = INTEL.run(self.args('latest', '--allow-network'), API, transport=transport, sleep=lambda _: None, now=NOW)
        API['validate']('intelligence', data)
        self.assertEqual(['CVE-2099-30059', 'CVE-2099-30005', 'CVE-2099-30007'], [r['id'] for r in data['records'][:3]])
        epss_ids = parse_qs(urlsplit([c for c in self.mock.calls if c[0] == 'epss'][0][1]).query)['cve'][0].split(',')
        self.assertEqual('CVE-2099-30059', epss_ids[0])  # EPSS budget goes to the top-ranked records.
        text = INTEL.markdown(data)
        self.assertEqual(50, text.count('\n### CVE-'))
        self.assertIn('30 more records', text)

    def test_live_cve_provenance_kev_epss_and_no_local_incident(self):
        data = self.run_intel('cve', 'CVE-2099-10001', '--allow-network')
        self.assertEqual(1, len(data['records']))
        record = data['records'][0]
        self.assertTrue(record['exploitation']['knownExploited'])
        self.assertEqual(0.91, record['exploitation']['epss'])
        self.assertEqual('2026-11-17', record['exploitation']['epssDate'])
        self.assertIsNone(record['exploitation']['epssModelVersion'])  # API version is not model version.
        self.assertEqual('Not assessed', record['applicability']['status'])
        self.assertEqual([], data['projectExposure'])
        for claim in record['claims']:
            self.assertTrue(claim['source']['url'].startswith('https://'))
            self.assertEqual(NOW, claim['source']['retrievedAt'])

    def test_immutable_snapshots_and_failed_refresh_keep_last_success(self):
        self.run_intel('cve', 'CVE-2099-10001', '--allow-network')
        store = STORE.Store(self.root / 'cache')
        original, _ = store.snapshot('nvd', {'cve': 'CVE-2099-10001'})
        self.mock.fail['nvd'] = 'HTTP_503'
        data = self.run_intel('cve', 'CVE-2099-10001', '--allow-network', now='2026-11-17T10:00:00+00:00')
        after, state = store.snapshot('nvd', {'cve': 'CVE-2099-10001'})
        self.assertEqual(original, after)
        self.assertEqual(NOW, state['lastSuccess'])
        row = next(s for s in data['sourceStatus'] if s['source'] == 'nvd')
        self.assertFalse(row['refreshSucceeded']); self.assertEqual('HTTP_503', row['lastAttemptError'])
        self.assertTrue(row['usedCachedSnapshot'])

    def test_offline_cache_age_and_no_refresh_or_network(self):
        self.run_intel('cve', 'CVE-2099-10001', '--allow-network')
        before = len(self.mock.calls)
        data = self.run_intel('cve', 'CVE-2099-10001', '--offline', now='2026-11-18T09:00:00+00:00')
        self.assertEqual(before, len(self.mock.calls))
        self.assertTrue(any(s['status'] == 'Stale' for s in data['sourceStatus']))
        self.assertTrue(data['records'])

    def test_latest_always_attempts_live_when_permitted(self):
        self.run_intel('latest', '--allow-network')
        before = len(self.mock.calls)
        self.run_intel('latest', '--allow-network')
        self.assertGreater(len(self.mock.calls), before)
        self.assertTrue(all(c[2] == 'GET' for c in self.mock.calls))

    def test_default_network_deny_and_status_never_probes(self):
        data = self.run_intel('cve', 'CVE-2099-10001')
        self.assertEqual([], self.mock.calls)
        self.assertEqual([], data['records'])
        self.assertTrue(all(s['lastAttemptError'] == 'NETWORK_NOT_AUTHORIZED' for s in data['sourceStatus']))
        status = self.run_intel('status', '--allow-network')
        self.assertEqual([], self.mock.calls)
        self.assertIn('Not tested', status['networkAvailability'])

    def test_invalid_registry_cannot_authorize_new_destination(self):
        file = self.root / 'registry.json'
        file.write_text(json.dumps({'schemaVersion': 'panda-recon.intel-sources/v1', 'sources': [
            {'id': 'nvd', 'endpoint': 'https://127.0.0.1/private', 'enabled': True, 'ttlSeconds': 60}]}))
        with self.assertRaises(ValueError): self.run_intel('latest', '--allow-network', '--sources', str(file))
        self.assertFalse(self.mock.calls)

    def test_source_ttl_configuration_and_disabled_state(self):
        file = self.root / 'registry.json'
        file.write_text(json.dumps({'schemaVersion': 'panda-recon.intel-sources/v1', 'sources': [
            {'id': 'nvd', 'ttlSeconds': 60}, {'id': 'kev', 'enabled': False}]}))
        self.run_intel('cve', 'CVE-2099-10001', '--allow-network', '--sources', str(file))
        data = self.run_intel('cve', 'CVE-2099-10001', '--offline', '--sources', str(file), now='2026-11-17T09:02:00+00:00')
        self.assertEqual('Stale', next(s for s in data['sourceStatus'] if s['source'] == 'nvd')['status'])
        self.assertEqual('Disabled', next(s for s in data['sourceStatus'] if s['source'] == 'kev')['status'])

    def test_package_queries_require_separate_opt_in(self):
        path = FIXTURE / 'components.json'
        data = self.run_intel('latest', '--allow-network', '--components', str(path))
        self.assertFalse(any(c[0] == 'osv' for c in self.mock.calls))
        self.assertEqual('Insufficient evidence', data['projectExposure'][0]['status'])
        data = self.run_intel('latest', '--allow-network', '--allow-package-queries', '--components', str(path))
        self.assertTrue(any(c[0] == 'osv' for c in self.mock.calls))
        self.assertEqual('Confirmed affected component', data['projectExposure'][0]['status'])
        self.assertEqual('Unverified', data['projectExposure'][0]['reachability'])
        self.assertEqual('Not established', data['projectExposure'][0]['localIncident'])
        self.assertFalse(any('demo-package' in r['url'] for r in data['requests']))  # Body not query string/logged.

    def test_alias_dedup_keeps_nvd_osv_claims(self):
        data = self.run_intel('latest', '--allow-network', '--allow-package-queries', '--components', str(FIXTURE / 'components.json'))
        self.assertEqual(1, len(data['records']))
        record = data['records'][0]
        self.assertEqual('CVE-2099-10001', record['id'])
        self.assertIn('GHSA-aaaa-bbbb-cccc', record['aliases'])
        self.assertEqual({'nvd', 'osv'}, {c['source']['sourceId'] for c in record['claims']})

    def test_supported_version_ranges_control_match_not_server_fuzzy_result(self):
        advisory = fixture('osv')['vulns'][0]
        for version, expected in [('1.1.0', 'Confirmed affected component'), ('1.2.0', 'Not affected'),
                                  ('2.0.0', 'Not affected'), (None, 'Version unknown')]:
            with self.subTest(version=version):
                component = {'ecosystem': 'npm', 'name': 'demo-package', 'version': version}
                self.assertEqual(expected, COMPONENTS.affected(component, advisory)[0])
        self.assertEqual('Insufficient evidence', COMPONENTS.affected({'ecosystem': 'Go', 'name': 'demo-package', 'version': '1.1.0'}, advisory)[0])

    def test_backport_declared_and_unsupported_ranges_remain_uncertain(self):
        advisory = fixture('osv')['vulns'][0]
        row = {'ecosystem': 'npm', 'name': 'demo-package', 'version': '1.1.0', 'backport': True}
        self.assertEqual('Insufficient evidence', COMPONENTS.affected(row, advisory)[0])
        row.pop('backport'); row['versionKind'] = 'declared'
        self.assertEqual('Potentially affected component', COMPONENTS.affected(row, advisory)[0])
        other = copy.deepcopy(advisory); other['affected'][0]['versions'] = []; other['affected'][0]['ranges'][0]['type'] = 'ECOSYSTEM'
        self.assertEqual('Potentially affected component', COMPONENTS.affected(dict(row, version='1.1.5'), other)[0])

    def test_semver_prereleases_and_last_affected(self):
        self.assertLess(COMPONENTS.semver('1.0.0-alpha.2'), COMPONENTS.semver('1.0.0-alpha.10'))
        self.assertLess(COMPONENTS.semver('1.0.0-rc.1'), COMPONENTS.semver('1.0.0'))
        self.assertEqual(COMPONENTS.semver('v1.0.0+build'), COMPONENTS.semver('1.0.0'))
        with self.assertRaises(ValueError): COMPONENTS.semver('1.0.0-01')

    def test_high_severity_kev_epss_do_not_override_unaffected(self):
        file = self.root / 'components.json'
        rows = fixture('components'); rows[0]['version'] = '1.2.0'; file.write_text(json.dumps(rows))
        data = self.run_intel('latest', '--allow-network', '--allow-package-queries', '--components', str(file))
        row = data['projectExposure'][0]
        self.assertEqual('Not affected', row['status'])
        self.assertEqual('No active match for this advisory', row['priority'])
        self.assertTrue(row['exploitation']['knownExploited'])

    def test_rejected_withdrawn_and_conflicting_states_are_retained(self):
        nvd = fixture('nvd'); nvd['vulnerabilities'][0]['cve']['vulnStatus'] = 'Rejected'
        self.mock.responses['nvd'] = (json.dumps(nvd).encode(), 'application/json')
        data = self.run_intel('latest', '--allow-network', '--allow-package-queries', '--components', str(FIXTURE / 'components.json'))
        self.assertTrue(data['records'][0]['conflictingStatus'])
        self.assertEqual('Insufficient evidence', data['projectExposure'][0]['status'])
        osv = fixture('osv'); osv['vulns'][0]['withdrawn'] = '2026-11-17T08:00:00Z'
        self.assertEqual('Not affected', COMPONENTS.affected(fixture('components')[0], osv['vulns'][0])[0])

    def test_latest_severity_filter_keeps_unknown_and_states_what_was_hidden(self):
        nvd = fixture('nvd'); base = nvd['vulnerabilities'][0]
        rows = []
        for cve_id, severity, score in (('CVE-2099-20001', 'CRITICAL', 9.8), ('CVE-2099-20002', 'MEDIUM', 5.0), ('CVE-2099-20003', None, None)):
            row = copy.deepcopy(base); row['cve']['id'] = cve_id
            if severity: row['cve']['metrics']['cvssMetricV31'][0]['cvssData'].update(baseSeverity=severity, baseScore=score)
            else: row['cve']['metrics'] = {}
            rows.append(row)
        nvd.update(vulnerabilities=rows, totalResults=3)
        self.mock.responses['nvd'] = (json.dumps(nvd).encode(), 'application/json')
        unfiltered = self.run_intel('latest', '--allow-network')
        self.assertEqual({'CVE-2099-20001', 'CVE-2099-20002', 'CVE-2099-20003'}, {r['id'] for r in unfiltered['records']})
        data = self.run_intel('latest', '--allow-network', '--severity', 'high')
        # Missing NVD enrichment is not low severity: the unknown record stays visible.
        self.assertEqual({'CVE-2099-20001', 'CVE-2099-20003'}, {r['id'] for r in data['records']})
        note = next(v for v in data['limitations'] if 'Severity filter' in v)
        self.assertIn('1 record', note); self.assertIn('without CVSS', note)
        self.assertIn('Severity filter', INTEL.markdown(data))
        self.assertEqual({'CVE-2099-20001'}, {r['id'] for r in self.run_intel('latest', '--allow-network', '--severity', 'critical')['records']} - {'CVE-2099-20003'})

    def test_missing_nvd_enrichment_is_not_unaffected(self):
        self.mock.fail['nvd'] = 'HTTP_403'
        data = self.run_intel('cve', 'CVE-2099-10001', '--allow-network')
        self.assertEqual(1, len(data['records']))  # KEV evidence remains, without invented CVSS.
        self.assertFalse(any(c['cvss'] for c in data['records'][0]['claims']))
        self.assertTrue(data['records'][0]['exploitation']['knownExploited'])

    def test_changed_and_invalid_response_preserves_valid_snapshot(self):
        self.run_intel('cve', 'CVE-2099-10001', '--allow-network')
        self.mock.responses['nvd'] = (b'{"unexpected":"schema"}', 'application/json')
        data = self.run_intel('cve', 'CVE-2099-10001', '--allow-network', now='2026-11-17T10:00:00+00:00')
        status = next(s for s in data['sourceStatus'] if s['source'] == 'nvd')
        self.assertEqual(NOW, status['lastSuccessfulSync'])
        self.assertFalse(status['refreshSucceeded'])
        self.assertTrue(data['records'])

    def test_incremental_nvd_changed_record_and_pagination_cap(self):
        self.run_intel('update', '--source', 'nvd', '--allow-network')
        data = fixture('nvd'); data['vulnerabilities'][0]['cve']['lastModified'] = '2026-11-17T10:00:00Z'
        self.mock.responses['nvd'] = (json.dumps(data).encode(), 'application/json')
        self.run_intel('update', '--source', 'nvd', '--allow-network', now='2026-11-17T10:00:00+00:00')
        query = parse_qs(urlsplit([c for c in self.mock.calls if c[0] == 'nvd'][-1][1]).query)
        self.assertIn('08:58:00', query['lastModStartDate'][0])
        store = STORE.Store(self.root / 'cache')
        snapshot, _ = store.snapshot('nvd', {'sync': True})
        self.assertEqual('2026-11-17T10:00:00Z', snapshot['data']['records'][0]['lastModified'])
        data['totalResults'] = 1000
        self.mock.responses['nvd'] = (json.dumps(data).encode(), 'application/json')
        failed = self.run_intel('update', '--source', 'nvd', '--allow-network', now='2026-11-17T11:00:00+00:00')
        self.assertTrue(next(s for s in failed['sourceStatus'] if s['source'] == 'nvd')['lastAttemptError'])
        self.assertEqual('2026-11-17T10:00:00+00:00', store.snapshot('nvd', {'sync': True})[0]['retrievedAt'])

    def test_owasp_dynamic_release_and_draft_not_guessed(self):
        data = self.run_intel('owasp', '--allow-network')
        web = next(r for r in data['records'] if r['id'] == 'owasp-web')
        self.assertEqual('2099', web['claims'][0]['details']['sourceVersion'])
        self.mock.responses['owasp-web'] = (b'<h1>Draft Top 10 2100, release candidate</h1>', 'text/html')
        data = self.run_intel('owasp', '--allow-network')
        web = next(r for r in data['records'] if r['id'] == 'owasp-web')
        self.assertIsNone(web['claims'][0]['details']['sourceVersion'])

    def test_incident_publication_date_is_not_occurrence_or_confirmation(self):
        data = self.run_intel('incidents', '--days', '7', '--allow-network')
        row = data['records'][0]
        self.assertEqual('advisory-lead', row['recordType'])
        details = row['claims'][0]['details']
        self.assertIsNone(details['occurredAt']); self.assertIsNone(details['firstDisclosureAt'])
        self.assertEqual([], details['confirmedFacts'])
        self.assertIsNotNone(row['claims'][0]['source']['publishedAt'])

    def test_rate_limit_retry_is_bounded_and_retry_after_is_respected(self):
        attempts = []; waits = []; clock = [0]
        def sleep(seconds): waits.append(seconds); clock[0] += seconds
        def transport(url, method, payload, timeout):
            attempts.append(url)
            if len(attempts) < 3: raise NET.SourceError('HTTP_429', 10)
            return b'{"ok":true}', 'application/json'
        client = NET.Client(self.mock.config, True, transport=transport, sleep=sleep, clock=lambda: clock[0])
        client.fetch('kev', self.mock.config['kev']['endpoint'])
        self.assertEqual(3, len(attempts)); self.assertEqual([10, 10], waits)
        client = NET.Client(self.mock.config, True, transport=lambda *a: (_ for _ in ()).throw(NET.SourceError('HTTP_429', 120)), sleep=sleep)
        with self.assertRaises(NET.SourceError): client.fetch('kev', self.mock.config['kev']['endpoint'])
        self.assertEqual(1, len(client.requests))

    def test_redirect_destinations_and_response_bounds_are_denied(self):
        with self.assertRaises(NET.SourceError): NET.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://collector.invalid')
        client = NET.Client(self.mock.config, True, transport=self.mock)
        with self.assertRaises(NET.SourceError): client.fetch('nvd', 'https://127.0.0.1/private')
        self.mock.responses['kev'] = (b'x' * (NET.MAX_BYTES + 1), 'application/json')
        with self.assertRaises(NET.SourceError): client.fetch('kev', self.mock.config['kev']['endpoint'])
        self.mock.responses['kev'] = ((FIXTURE / 'kev.json').read_bytes(), 'text/plain; charset=utf-8')
        self.assertTrue(client.fetch('kev', self.mock.config['kev']['endpoint']).startswith(b'{'))
        self.mock.responses['kev'] = (b'<html>not JSON</html>', 'text/html')
        with self.assertRaises(NET.SourceError): client.fetch('kev', self.mock.config['kev']['endpoint'])

    def test_cache_tamper_fails_without_repairing_reference(self):
        self.run_intel('cve', 'CVE-2099-10001', '--allow-network')
        store = STORE.Store(self.root / 'cache')
        _, state = store.snapshot('nvd', {'cve': 'CVE-2099-10001'})
        path = self.root / 'cache' / state['snapshot']; path.write_text('{}')
        with self.assertRaises(ValueError): store.snapshot('nvd', {'cve': 'CVE-2099-10001'})

    def test_reports_quote_sources_and_do_not_activate_embedded_instructions(self):
        data = self.run_intel('cve', 'CVE-2099-10001', '--allow-network')
        text = INTEL.markdown(data)
        self.assertNotIn('](', text.replace('](https://services.nvd.nist.gov', '').replace('](https://raw.githubusercontent.com', '').replace('](https://api.first.org', ''))
        self.assertTrue(all(c[0] in {'nvd', 'kev', 'epss'} for c in self.mock.calls))
        out = self.root / 'report'; INTEL.write(data, out)
        self.assertTrue((out / 'CVE_ANALYSIS.md').exists())
        self.assertFalse((out / 'THREAT_INTELLIGENCE.md').exists())
        self.assertEqual(0o600, (out / 'intelligence.json').stat().st_mode & 0o777)
        with self.assertRaises(FileExistsError): INTEL.write(data, out)

    def test_inventory_is_local_exact_and_does_not_copy_resolved_credentials(self):
        root = self.root / 'project'; root.mkdir()
        (root / 'package-lock.json').write_text(json.dumps({'lockfileVersion': 3, 'packages': {
            '': {'name': 'private-root'}, 'node_modules/demo-package': {'version': '1.1.0', 'resolved': 'https://secret@registry.invalid/'}}}))
        rows = COMPONENTS.inventory(root, API['load_json'])
        self.assertEqual(['demo-package'], [r['name'] for r in rows])
        self.assertNotIn('secret@', json.dumps(rows))
        self.assertEqual('resolved', rows[0]['versionKind'])

    def test_intel_requests_and_live_offline_conflicts(self):
        contract = API['load_json'](ROOT / 'skills/panda-recon/assets/command-contract.json')
        commands = API['support']('commands')
        for topic in contract['intelTopics']:
            values = ['intel', topic] + (['CVE-2099-10001'] if topic == 'cve' else [])
            self.assertFalse(commands.parse_request(values, contract)['executed'])
        for mode in ('scan', 'hunt', 'incident'):
            result = commands.parse_request([mode, str(FIXTURE), '--intel', 'live'], contract)
            self.assertEqual('public-intelligence-only', result['options']['networkScope'])
            with self.assertRaises(ValueError): commands.parse_request([mode, str(FIXTURE), '--offline', '--intel', 'live'], contract)


if __name__ == '__main__': unittest.main(verbosity=2)
