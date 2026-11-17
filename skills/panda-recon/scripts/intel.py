"""On-demand public intelligence, dated private snapshots and conservative relevance."""

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import html
import json
import os
from pathlib import Path
import re
import uuid

TOPICS = ['latest', 'update', 'status', 'owasp', 'cve', 'kev', 'incidents']


def parser(prog='panda-recon intel'):
    result = argparse.ArgumentParser(prog=prog, description=__doc__)
    result.add_argument('topic', choices=TOPICS)
    result.add_argument('identifier', nargs='?')
    result.add_argument('--cache', type=Path, default=Path('.panda-suite/recon/intelligence-cache'))
    result.add_argument('--sources', type=Path, help='registry override: known source IDs/endpoints only; configurable enabled/TTL')
    result.add_argument('--source', action='append', help='select known source IDs for latest/update')
    result.add_argument('--days', type=int, default=7)
    result.add_argument('--ecosystem', choices=['go', 'npm', 'pypi'])
    result.add_argument('--severity', choices=['critical', 'high', 'medium', 'low', 'informational'])
    result.add_argument('--offline', action='store_true')
    result.add_argument('--allow-network', action='store_true', help='explicit public-source retrieval permission; no target probing')
    result.add_argument('--allow-package-queries', action='store_true', help='also permit sending supplied exact package names/versions to OSV')
    result.add_argument('--components', type=Path, help='reviewed local JSON component array; no automatic upload')
    result.add_argument('--project', type=Path, help='derive npm package-lock v2/v3 inventory locally')
    result.add_argument('--output', type=Path, help='new private directory; no previous report overwritten')
    return result


def configuration(api, path=None):
    default = api['load_json'](api['BASE'] / 'assets/intelligence-sources.json')
    base = {s['id']: s for s in default['sources']}
    if path:
        override = api['load_json'](path)
        if override.get('schemaVersion') != default['schemaVersion'] or not isinstance(override.get('sources'), list):
            raise ValueError('invalid intelligence registry')
        seen = set()
        for row in override['sources']:
            name = row.get('id')
            if (name not in base or name in seen or row.get('endpoint', base[name]['endpoint']) != base[name]['endpoint']
                    or type(row.get('ttlSeconds', base[name]['ttlSeconds'])) is not int
                    or not 60 <= row.get('ttlSeconds', base[name]['ttlSeconds']) <= 30 * 86400
                    or type(row.get('enabled', True)) is not bool):
                raise ValueError('unapproved endpoint or invalid source policy')
            seen.add(name)
            base[name] = dict(base[name], ttlSeconds=row.get('ttlSeconds', base[name]['ttlSeconds']), enabled=row.get('enabled', True))
    return base


def source_read(name, query, config, store, client, api, now, live, package_allowed=False):
    policy = config[name]; module = api['support']('intel_store')
    snapshot, state = store.snapshot(name, query)
    status = {'source': name, 'enabled': policy['enabled'], 'endpoint': policy['endpoint'],
              'lastSuccessfulSync': state.get('lastSuccess') if state else None,
              'lastAttemptError': state.get('lastError') if state else None, 'refreshSucceeded': False,
              'sourceVersion': snapshot['data'].get('sourceVersion') if snapshot else None,
              **module.freshness(snapshot, policy['ttlSeconds'], now)}
    if not policy['enabled']:
        status['status'] = 'Disabled'; return None, status
    if live:
        error = None
        try:
            if name == 'osv' and not package_allowed: raise ValueError('PACKAGE_QUERY_NOT_AUTHORIZED')
            if not client.allow_network: raise ValueError('NETWORK_NOT_AUTHORIZED')
            data = api['support']('intel_sources').fetch(name, query, client, config, now, snapshot)
            if not isinstance(data.get('records'), list) or len(data['records']) > 5000:
                raise ValueError('SOURCE_RECORD_LIMIT')
            if data.get('sourceVersion') is not None and not isinstance(data['sourceVersion'], str):
                raise ValueError('source version schema changed')
            # Validate the normalized view before changing the successful cache pointer.
            temporary = normalize([(name, {'data': data, 'retrievedAt': now})], config, now)
            api['validate']('intelligence', {'schemaVersion': 'panda-recon.intelligence/v1', 'generatedAt': now,
                'topic': 'update', 'records': temporary, 'sourceStatus': [], 'projectExposure': [],
                'requests': [], 'networkAvailability': 'Source validation only', 'limitations': []})
            previous_version = snapshot['data'].get('sourceVersion') if snapshot else None
            store.commit(name, query, now, data=data)
            snapshot, state = store.snapshot(name, query)
            status.update(lastSuccessfulSync=now, lastAttemptError=None, refreshSucceeded=True,
                          sourceVersion=data.get('sourceVersion'), previousSourceVersion=previous_version,
                          versionChanged=previous_version is not None and data.get('sourceVersion') is not None and previous_version != data['sourceVersion'],
                          **module.freshness(snapshot, policy['ttlSeconds'], now))
        except (ValueError, OSError, KeyError, TypeError, AttributeError, json.JSONDecodeError) as failure:
            error = getattr(failure, 'code', None)
            if error is None:
                error = str(failure) if str(failure) in {'NETWORK_NOT_AUTHORIZED', 'PACKAGE_QUERY_NOT_AUTHORIZED'} else 'SOURCE_RESPONSE_INVALID_OR_UNAVAILABLE'
            if client.allow_network:
                store.commit(name, query, now, error=error)  # Never replaces a successful snapshot.
            status['lastAttemptError'] = error
    status['usedCachedSnapshot'] = snapshot is not None and not status['refreshSucceeded']
    status['networkAvailability'] = 'Observed response' if status['refreshSucceeded'] else 'Not verified'
    return snapshot, status


def provenance(source, data, retrieved, policy, published=None, modified=None):
    return {'name': policy['name'], 'sourceId': source, 'url': data['urls'][0],
            'retrievedAt': retrieved, 'publishedAt': published, 'modifiedAt': modified,
            'sourceVersion': data.get('sourceVersion'), 'tier': 'primary', 'verification': 'Retrieved source assertion, not local exploitation proof'}


def normalize(snapshots, config, now, requested_cve=None):
    adapters = []
    for source, snapshot in snapshots:
        data, retrieved = snapshot['data'], snapshot['retrievedAt']
        if source == 'nvd':
            for raw in data['records']:
                descriptions = [d['value'] for d in raw['descriptions'] if d.get('lang') == 'en']
                metrics = []
                for group in raw.get('metrics', {}).values():
                    for metric in group:
                        cvss = metric.get('cvssData', {})
                        score = cvss.get('baseScore')
                        if score is not None and (type(score) not in (int, float) or not 0 <= score <= 10):
                            raise ValueError('invalid CVSS score')
                        metrics.append({'score': score, 'version': cvss.get('version'), 'vector': cvss.get('vectorString'),
                                        'severity': cvss.get('baseSeverity') or metric.get('baseSeverity')})
                adapters.append({'id': raw['id'], 'aliases': [], 'recordType': 'vulnerability',
                                 'title': (descriptions[0] if descriptions else 'Description unavailable')[:4000],
                                 'recordStatus': raw.get('vulnStatus', 'Unknown'), 'affected': [], 'cvss': metrics,
                                 'affectedProducts': raw.get('configurations', []),
                                 'vendorReferences': raw.get('references', []),
                                 'source': provenance(source, data, retrieved, config[source],
                                     api_iso(raw['published']), api_iso(raw['lastModified']))})
        elif source == 'osv':
            for raw in data['records']:
                ids = [raw['id'], *raw.get('aliases', [])]
                if any(not isinstance(v, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}', v) for v in ids):
                    raise ValueError('unsafe advisory identifier')
                cves = sorted(v for v in ids if re.fullmatch(r'CVE-\d{4}-\d{4,19}', v))
                adapters.append({'id': cves[0] if cves else raw['id'], 'aliases': sorted(set(ids) - set(cves[:1])),
                                 'recordType': 'vulnerability', 'title': str(raw.get('summary') or raw.get('details') or raw['id'])[:4000],
                                 'recordStatus': 'Withdrawn' if raw.get('withdrawn') else 'Published', 'withdrawn': raw.get('withdrawn'),
                                 'affected': raw['affected'], 'cvss': [],
                                 'source': provenance(source, data, retrieved, config[source], raw.get('published'), raw.get('modified'))})
        elif source == 'kev' and requested_cve:
            for raw in data['records']:
                if raw['cveID'] == requested_cve:
                    adapters.append({'id': requested_cve, 'aliases': [], 'recordType': 'vulnerability',
                        'title': raw.get('vulnerabilityName', 'KEV entry'), 'recordStatus': 'Known exploited catalog entry',
                        'affected': [], 'cvss': [], 'dateAdded': raw['dateAdded'], 'requiredAction': raw['requiredAction'],
                        'source': provenance(source, data, retrieved, config[source])})
        elif source not in ('kev', 'epss'):
            for raw in data['records']:
                adapters.append({'id': str(raw['id']), 'aliases': [],
                                 'recordType': 'advisory-lead' if source == 'incidents' else 'guidance',
                                 'title': str(raw.get('title', raw['id']))[:4000], 'recordStatus': 'Requires primary-source interpretation',
                                 'affected': [], 'cvss': [], 'details': raw,
                                 'source': provenance(source, data, retrieved, config[source], raw.get('publishedAt'), raw.get('modifiedAt'))})
    result = []
    for claim in adapters:
        identities = {claim['id'], *claim['aliases']}
        matches = [r for r in result if identities & {r['id'], *r['aliases']}]
        if matches:
            primary = matches[0]
            for other in matches[1:]:
                primary['claims'] += other['claims']; identities.update([other['id'], *other['aliases']]); result.remove(other)
            identities.update([primary['id'], *primary['aliases']]); primary['claims'].append(claim)
        else:
            primary = {'id': claim['id'], 'aliases': [], 'recordType': claim['recordType'], 'claims': [claim]}
            result.append(primary)
        cves = sorted(v for v in identities if re.fullmatch(r'CVE-\d{4}-\d{4,19}', v))
        primary['id'] = cves[0] if cves else sorted(identities)[0]
        primary['aliases'] = sorted(identities - {primary['id']})
    kev = next((s for source, s in snapshots if source == 'kev'), None)
    epss = [s for source, s in snapshots if source == 'epss']
    for record in result:
        ids = {record['id'], *record['aliases']}
        record['retrievedAt'] = max(c['source']['retrievedAt'] for c in record['claims'])
        record['exploitation'] = {'knownExploited': None, 'kevCatalogDate': None, 'epss': None,
                                  'epssDate': None, 'epssModelVersion': None, 'epssDateStale': None}
        if record['recordType'] == 'vulnerability':
            if kev:
                record['exploitation'].update(knownExploited=any(r['cveID'] in ids for r in kev['data']['records']), kevCatalogDate=kev['data'].get('catalogDate'))
                record.setdefault('enrichmentSources', []).append(provenance('kev', kev['data'], kev['retrievedAt'], config['kev']))
            for snapshot in epss:
                for row in snapshot['data']['records']:
                    if row['cve'] in ids:
                        record['exploitation'].update(epss=float(row['epss']), epssDate=row['date'],
                            epssModelVersion=snapshot['data'].get('modelVersion'),
                            epssDateStale=(datetime.fromisoformat(now).date() - datetime.fromisoformat(row['date']).date()).days > 2)
                        record.setdefault('enrichmentSources', []).append(provenance('epss', snapshot['data'], snapshot['retrievedAt'], config['epss']))
        states = {c['recordStatus'] for c in record['claims']}
        inactive = {'Rejected', 'Withdrawn'}
        record['conflictingStatus'] = bool(states & inactive and states - inactive)
        scores_by_version = {}
        for claim in record['claims']:
            for metric in claim['cvss']:
                if metric['score'] is not None: scores_by_version.setdefault(metric['version'], set()).add(metric['score'])
        record['conflictingScores'] = any(len(scores) > 1 for scores in scores_by_version.values())
        record['applicability'] = {'status': 'Not assessed', 'evidence': []}
        ages = [(datetime.fromisoformat(now) - datetime.fromisoformat(c['source']['retrievedAt'])).total_seconds()
                for c in record['claims']]
        record['dataFreshness'] = 'Fresh' if all(0 <= age < config[c['source']['sourceId']]['ttlSeconds']
                                                for age, c in zip(ages, record['claims'])) else 'Stale'
    return result


def api_iso(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return (parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)).isoformat()


def exposures(records, components, api):
    rows = []
    for component in components:
        matched = False
        for record in records:
            if record['recordType'] != 'vulnerability': continue
            candidates = [c for c in record['claims'] if c['source']['sourceId'] == 'osv'
                          and any(a.get('package', {}).get('ecosystem') == component['ecosystem']
                                  and a.get('package', {}).get('name') == component['name'] for a in c['affected'])]
            if not candidates: continue
            matched = True
            answers = [api['support']('components').affected(component, c) for c in candidates]
            if record['conflictingStatus'] or len({a[0] for a in answers}) > 1:
                status, reason = 'Insufficient evidence', 'Contradictory source states/applicability retained; inspect dated authority.'
            else: status, reason = answers[0]
            if status == 'Confirmed affected component' and record.get('dataFreshness') == 'Stale':
                status, reason = 'Potentially affected component', 'Stored version match is stale; current advisory state requires refresh.'
            if status == 'Confirmed affected component' and record['exploitation']['knownExploited']:
                priority = 'Urgent review'; reasons = ['Supported affected component and KEV membership; no local compromise established.']
            elif status == 'Confirmed affected component':
                priority = 'Prioritize remediation review'; reasons = ['Supported affected component; verify deployment, reachability, prerequisites and mitigations.']
            elif status == 'Not affected': priority, reasons = 'No active match for this advisory', ['Not affected result is advisory-scoped; high CVSS/EPSS cannot override it.']
            else: priority, reasons = 'Verify applicability', ['Evidence gap prevents an exploitable-component conclusion.']
            if component.get('internetExposed') is True: reasons.append('Operator-supplied internet exposure; not independently observed.')
            if component.get('criticality'): reasons.append('Operator-supplied asset criticality: ' + str(component['criticality']))
            if record['exploitation']['epss'] is not None:
                reasons.append('EPSS probability ' + str(record['exploitation']['epss']) + ' dated ' + str(record['exploitation']['epssDate']) + '; stale=' + str(record['exploitation']['epssDateStale']) + '; not proof of attack.')
            row = {'component': component, 'advisoryId': record['id'], 'aliases': record['aliases'], 'status': status,
                   'evidence': [reason], 'exploitation': record['exploitation'], 'priority': priority, 'priorityReasons': reasons,
                   'reachability': 'Unverified', 'localIncident': 'Not established',
                   'sourceUrls': sorted({c['source']['url'] for c in candidates})}
            row['affectedRanges'] = [interval for c in candidates for a in c['affected']
                                     if a.get('package', {}).get('ecosystem') == component['ecosystem'] and a.get('package', {}).get('name') == component['name']
                                     for interval in a.get('ranges', [])]
            row['upstreamFixedVersions'] = sorted({event['fixed'] for interval in row['affectedRanges']
                                                  for event in interval.get('events', []) if isinstance(event.get('fixed'), str)})
            rows.append(row)
        if not matched:
            rows.append({'component': component, 'advisoryId': None, 'aliases': [],
                         'status': 'Version unknown' if not component['version'] else 'Insufficient evidence',
                         'evidence': ['No exact advisory identity in available records; not proof of no vulnerabilities.'],
                         'exploitation': None, 'priority': 'Gather evidence', 'priorityReasons': ['Need authoritative complete package/version data.'],
                         'reachability': 'Unverified', 'localIncident': 'Not established', 'sourceUrls': []})
    return rows


def run(args, api, transport=None, sleep=None, now=None):
    if not 1 <= args.days <= 120: raise ValueError('days must be 1–120')
    if args.offline and args.allow_network: raise ValueError('offline conflicts with network permission')
    if args.topic == 'cve': api['support']('intel_sources').cve_id(args.identifier)
    elif args.identifier is not None: raise ValueError('unexpected intelligence identifier')
    now = api_iso(now or datetime.now(timezone.utc).isoformat())
    config = configuration(api, args.sources)
    store = api['support']('intel_store').Store(args.cache)
    kwargs = {} if transport is None else {'transport': transport}
    if sleep is not None: kwargs['sleep'] = sleep
    client = api['support']('intel_net').Client(config, args.allow_network and not args.offline, **kwargs)
    if args.topic == 'status':
        entries = store.state()['entries']; statuses = []
        for name, policy in config.items():
            related = [e for e in entries.values() if e.get('source') == name]
            for entry in related or [{}]:
                snapshot, _ = store.snapshot(name, entry['query']) if entry else (None, None)
                statuses.append({'source': name, 'enabled': policy['enabled'], 'endpoint': policy['endpoint'],
                    'lastSuccessfulSync': entry.get('lastSuccess'), 'lastAttemptError': entry.get('lastError'),
                    'sourceVersion': snapshot['data'].get('sourceVersion') if snapshot else None,
                    **api['support']('intel_store').freshness(snapshot, policy['ttlSeconds'], now)})
        return {'schemaVersion': 'panda-recon.intelligence/v1', 'generatedAt': now, 'topic': 'status',
                'records': [], 'sourceStatus': statuses, 'projectExposure': [], 'requests': [],
                'networkAvailability': 'Not tested; status does not probe providers', 'limitations': ['A skill is not continuous monitoring; no scheduler was activated.']}
    components = []
    if args.components: components = api['support']('components').validate(api['load_json'](args.components))
    elif args.project:
        if args.project.is_symlink() or not args.project.is_dir(): raise ValueError('invalid project root')
        components = api['support']('components').inventory(args.project.resolve(), api['load_json'])
    if args.ecosystem:
        wanted = api['support']('components').ECOSYSTEMS[args.ecosystem]
        components = [c for c in components if c['ecosystem'] == wanted]
    snapshots, statuses = [], []
    def obtain(name, query):
        snapshot, status = source_read(name, query, config, store, client, api, now,
                                      live=not args.offline, package_allowed=args.allow_package_queries)
        statuses.append(status)
        if snapshot: snapshots.append((name, snapshot))
    if args.source:
        selected = args.source
        if len(set(selected)) != len(selected) or any(s not in config for s in selected): raise ValueError('unknown/repeated source selection')
    elif args.topic == 'owasp': selected = ['owasp-web', 'owasp-api', 'owasp-asvs']
    elif args.topic == 'incidents': selected = ['incidents']
    elif args.topic == 'kev': selected = ['kev']
    elif args.topic == 'update': selected = ['nvd', 'kev', 'owasp-web', 'owasp-api', 'owasp-asvs', 'mitre']
    else: selected = ['nvd', 'kev']
    for source in selected:
        if source == 'osv': continue  # Only explicit reviewed package/version queries below.
        if source == 'epss':
            if not args.identifier: raise ValueError('EPSS direct selection requires cve topic')
            query = {'cves': [args.identifier]}
        elif source == 'nvd': query = {'cve': args.identifier} if args.identifier else {'days': args.days, 'sync': args.topic == 'update'}
        else: query = {}
        obtain(source, query)
    ids = [args.identifier] if args.identifier else sorted({row['id'] for source, s in snapshots if source == 'nvd' for row in s['data']['records']})[:50]
    if ids and args.topic in ('cve', 'latest', 'update') and 'epss' not in selected:
        obtain('epss', {'cves': ids})
    for component in components[:20]:
        if component['version']:
            obtain('osv', {'package': {'name': component['name'], 'ecosystem': component['ecosystem']}, 'version': component['version']})
    extra_ids = sorted({alias for source, snapshot in snapshots if source == 'osv' for row in snapshot['data']['records']
                        for alias in [row['id'], *row.get('aliases', [])]
                        if re.fullmatch(r'CVE-\d{4}-\d{4,19}', alias)} - set(ids))[:50]
    if extra_ids and args.topic in ('cve', 'latest', 'update'):
        obtain('epss', {'cves': extra_ids})
    records = normalize(snapshots, config, now, requested_cve=args.identifier)
    if args.topic == 'kev' and snapshots:
        data = next((s for source, s in snapshots if source == 'kev'), None)
        if data:
            for raw in data['data']['records']:
                if raw['cveID'] not in {r['id'] for r in records}:
                    records.append({'id': raw['cveID'], 'aliases': [], 'recordType': 'vulnerability',
                        'retrievedAt': data['retrievedAt'], 'claims': [{'id': raw['cveID'], 'title': raw.get('vulnerabilityName', 'KEV entry'),
                            'recordStatus': 'KEV membership; full CVE record not loaded', 'affected': [], 'cvss': [],
                            'requiredAction': raw['requiredAction'], 'dateAdded': raw['dateAdded'],
                            'source': provenance('kev', data['data'], data['retrievedAt'], config['kev'])}],
                        'exploitation': {'knownExploited': True, 'kevCatalogDate': data['data'].get('catalogDate'),
                            'epss': None, 'epssDate': None, 'epssModelVersion': None, 'epssDateStale': None},
                        'conflictingStatus': False, 'conflictingScores': False, 'applicability': {'status': 'Not assessed', 'evidence': []}})
    if args.topic == 'incidents':
        threshold = datetime.fromisoformat(now) - timedelta(days=args.days)
        records = [r for r in records if any(c['source']['publishedAt'] is None or datetime.fromisoformat(c['source']['publishedAt']) >= threshold for c in r['claims'])]
    exposure = exposures(records, components, api)  # Before filtering: an affected component never disappears.
    severity_note = []
    if args.severity:
        records, severity_note = severity_filter(records, args.severity)
    return {'schemaVersion': 'panda-recon.intelligence/v1', 'generatedAt': now, 'topic': args.topic,
            'records': records, 'sourceStatus': statuses, 'projectExposure': exposure,
            'requests': client.requests, 'networkAvailability': 'Network permitted for fixed sources' if client.allow_network else 'Offline or not authorized',
            'limitations': ['External intelligence is not a local incident or proof of exploit reachability.',
                'TTL measures retrieval age, not provider publication completeness; outages preserve prior snapshots.',
                'EPSS is a dated probability, separate from CVSS severity and KEV known exploitation.',
                'Absence from KEV is not proof that exploitation never occurred.',
                'OWASP projects are interpreted separately; incident feed items are leads, not confirmed breaches.',
                'No daemon, scheduler, package upgrade, target probe or alert delivery was activated.',
                'Package matching supports exact versions and npm/Go SEMVER only; other ranges/backports remain uncertain.',
                'NVD latest is a bounded modification window, not a complete all-time catalog; publication/modification dates remain distinct.'] + severity_note}


SEVERITY_ORDER = ['informational', 'low', 'medium', 'high', 'critical']


def record_severity(record):
    """Highest publisher severity across claims, or None when no CVSS severity was published."""
    ranks = [SEVERITY_ORDER.index('informational' if s == 'none' else s)
             for claim in record['claims'] for metric in claim.get('cvss', [])
             for s in [str(metric.get('severity') or '').lower()] if s in SEVERITY_ORDER or s == 'none']
    return SEVERITY_ORDER[max(ranks)] if ranks else None


def severity_filter(records, minimum):
    """Display filter on publisher CVSS severity. Records without CVSS stay: missing enrichment is not low."""
    floor = SEVERITY_ORDER.index(minimum)
    kept, hidden, unknown = [], 0, 0
    for record in records:
        severity = record_severity(record)
        if severity is None: unknown += 1; kept.append(record)
        elif SEVERITY_ORDER.index(severity) >= floor: kept.append(record)
        else: hidden += 1
    note = (f'Severity filter {minimum} and above: {hidden} record{"" if hidden == 1 else "s"} below it omitted; '
            f'{unknown} record{"" if unknown == 1 else "s"} without CVSS severity kept because missing enrichment is not low severity. '
            'Project exposure is computed before filtering.')
    return kept, [note]


def markdown(data):
    def safe(value):
        text = html.escape(str(value), quote=False).replace('\n', ' / ')
        return re.sub(r'([\\`*_{}\[\]()#+!|>])', r'\\\1', text)
    lines = ['# Threat intelligence', '', 'Assessment time (UTC): ' + safe(data['generatedAt']),
             '', '## Source freshness', '']
    for source in data['sourceStatus']:
        lines.append('- ' + safe(source['source']) + ': ' + safe(source['status']) + '; last success ' + safe(source.get('lastSuccessfulSync')) + '; last error ' + safe(source.get('lastAttemptError')))
    lines += ['', '## Executive summary', '',
              f'{len(data["records"])} source records; {len(data["projectExposure"])} component assessments. This is not proof of a local compromise.',
              '', '## Vulnerabilities, guidance and reported leads', '']
    urls = []
    for record in data['records']:
        lines += ['### ' + safe(record['id']), '', 'Type: ' + safe(record['recordType'])]
        for claim in record['claims']:
            source = claim['source']; urls.append(source['url'])
            lines += ['- ' + safe(claim.get('title', record['id'])),
                      '- Source state: ' + safe(claim['recordStatus']) + '; published ' + safe(source.get('publishedAt')) + '; modified ' + safe(source.get('modifiedAt')) + '; retrieved ' + safe(source['retrievedAt'])]
        if 'exploitation' in record:
            ex = record['exploitation']; lines += ['- KEV: ' + safe(ex['knownExploited']) + '; EPSS: ' + safe(ex['epss']) + ' dated ' + safe(ex['epssDate']) + ' (probability, not observed attack).']
            urls += [s['url'] for s in record.get('enrichmentSources', [])]
    lines += ['', '## Project exposure and defensive next steps', '']
    for row in data['projectExposure']:
        component = row['component']
        lines += ['- ' + safe(component['ecosystem'] + ':' + component['name'] + '@' + str(component['version'])) + ': ' + safe(row['status']) + '; ' + safe(row['priority'])]
        lines += ['  ' + safe(reason) for reason in row['evidence'] + row['priorityReasons']]
    lines += ['', '## Authoritative request references', '']
    # Only adapter-generated fixed-endpoint URLs; never advisory-supplied URLs or images.
    for i, url in enumerate(sorted(set(urls)), 1):
        lines.append(f'- [Source {i}]({url})')
    lines += ['', '## Limits', ''] + ['- ' + safe(v) for v in data['limitations']]
    return '\n'.join(lines) + '\n'


def write(data, output):
    output = Path(output).absolute()
    for parent in [output, *output.parents]:
        if parent.is_symlink(): raise ValueError('linked intelligence output refused')
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700); output.mkdir(mode=0o700)
    report_name = {'cve': 'CVE_ANALYSIS.md', 'owasp': 'OWASP_UPDATES.md', 'incidents': 'INCIDENT_INTELLIGENCE.md'}.get(data['topic'], 'THREAT_INTELLIGENCE.md')
    contents = {'intelligence.json': json.dumps(data, indent=2, ensure_ascii=True, allow_nan=False) + '\n',
                'source-status.json': json.dumps(data['sourceStatus'], indent=2, ensure_ascii=True, allow_nan=False) + '\n',
                report_name: markdown(data)}
    if data['projectExposure']:
        lines = ['# Project exposure', '', 'Assessed at ' + data['generatedAt'] + '. No local incident or reachability is established.', '']
        def clean(value): return re.sub(r'[^A-Za-z0-9 @:._/,=+? -]', '?', str(value))
        for row in data['projectExposure']:
            ex = row['exploitation'] or {}
            lines += ['## ' + clean(row['component']['name']), '',
                      '- Version: ' + clean(row['component']['version']) + '; ecosystem: ' + clean(row['component']['ecosystem']),
                      '- Advisory: ' + clean(row['advisoryId']) + '; affected status: ' + row['status'],
                      '- KEV: ' + clean(ex.get('knownExploited')) + '; EPSS: ' + clean(ex.get('epss')) + ' dated ' + clean(ex.get('epssDate')),
                      '- Priority: ' + row['priority'], '- Upstream fixed versions (not vendor/backport advice): ' + clean(row.get('upstreamFixedVersions', []))]
            lines += ['- ' + clean(reason) for reason in row['evidence'] + row['priorityReasons']]
            lines += ['- Range records: ' + clean(row.get('affectedRanges', [])), '']
        lines += ['See intelligence.json for exact dated source URLs, ranges and evidence; suggested upstream fixes need deployment/vendor verification.']
        contents['PROJECT_EXPOSURE.md'] = '\n'.join(lines) + '\n'
    for name, text in contents.items():
        descriptor = os.open(output / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream: stream.write(text)
    return {'files': list(contents), 'recordCount': len(data['records']), 'sourceCount': len(data['sourceStatus']),
            'networkRequests': len(data['requests']), 'monitoringActive': False}
