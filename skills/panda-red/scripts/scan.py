"""Bounded local discovery, imported finding normalization and scan report views.

No scanner, network, shell, package installation or target execution occurs here.
"""

from datetime import datetime, timezone
import copy
import fnmatch
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import stat
import uuid

SEVERITIES = ['Informational', 'Low', 'Medium', 'High', 'Critical']
MAX_FILE = 1024 * 1024


def digest(value):
    return hashlib.sha256(value).hexdigest()


def scrub(value, secrets=()):
    if isinstance(value, str):
        for secret in sorted(set(secrets), key=len, reverse=True):
            if secret:
                value = value.replace(secret, '[REDACTED]')
        value = re.sub(r'-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----', '[REDACTED PRIVATE KEY]', value, flags=re.S)
        value = re.sub(r'\b(?:AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})\b', '[REDACTED]', value)
        value = re.sub(r'(?i)\b(bearer)\s+[A-Za-z0-9._~+/-]+', r'\1 [REDACTED]', value)
        value = re.sub(r'''(?i)\b(password|api[_-]?key|token|secret)\s*[:=]\s*["']?[^\s"';,}]+''', r'\1=[REDACTED]', value)
        return ''.join(c for c in value if c in '\n\t' or ord(c) >= 32)
    if isinstance(value, list):
        return [scrub(item, secrets) for item in value]
    if isinstance(value, dict):
        return {key: scrub(item, secrets) for key, item in value.items()}
    return value


def excluded(path, patterns):
    for pattern in patterns:
        base = pattern[:-3] if pattern.endswith('/**') else pattern.rstrip('/')
        if path == base or path.startswith(base + '/') or fnmatch.fnmatchcase(path, pattern):
            return True
    return False


def local_file(root, name, patterns):
    if not isinstance(name, str) or not name or '\\' in name or '\x00' in name:
        raise ValueError('unsafe source location')
    path = Path(name)
    if path.is_absolute():
        try:
            path = path.relative_to(root)
        except ValueError as error:
            raise ValueError('source outside target') from error
    if any(p in {'', '.', '..'} for p in str(path).split('/')):
        raise ValueError('unsafe source location')
    relative = path.as_posix()
    if excluded(relative, ['.git', *patterns]):
        raise ValueError('source excluded from requested scope')
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('linked source refused')
    info = current.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_FILE:
        raise ValueError('unsupported source file')
    with current.open('rb') as stream:
        content = stream.read(MAX_FILE + 1)
    if len(content) > MAX_FILE:
        raise ValueError('source size limit exceeded')
    return relative, content


def discover(root, depth, patterns):
    limit, entry_limit = (128, 5000) if depth == 'quick' else (2048, 20000)
    byte_limit = (8 if depth == 'quick' else 32) * MAX_FILE
    files, skipped, entries, total_bytes = [], [], 0, 0
    def walk_error(error):
        try:
            relative = Path(error.filename).relative_to(root).as_posix()
        except (TypeError, ValueError):
            relative = '<unreadable-directory>'
        skipped.append({'path': relative, 'reason': 'directory could not be inspected; permission or filesystem error'})
    for directory, dirs, names in os.walk(root, followlinks=False, onerror=walk_error):
        dirs.sort(); names.sort()
        kept = []
        for name in dirs:
            path = Path(directory) / name
            rel = path.relative_to(root).as_posix()
            entries += 1
            if entries > entry_limit:
                return files, skipped, True
            if path.is_symlink() or excluded(rel, ['.git', *patterns]):
                skipped.append({'path': rel, 'reason': 'symlink or explicit/default .git exclusion'})
            else:
                kept.append(name)
        dirs[:] = kept
        for name in names:
            entries += 1
            path = Path(directory) / name
            rel = path.relative_to(root).as_posix()
            if excluded(rel, ['.git', *patterns]):
                skipped.append({'path': rel, 'reason': 'explicit/default .git exclusion'})
                continue
            if len(files) >= limit or entries > entry_limit:
                return files, skipped, True
            try:
                rel, content = local_file(root, rel, patterns)
                total_bytes += len(content)
                if total_bytes > byte_limit:
                    return files, skipped, True
                files.append({'path': rel, 'bytes': len(content), 'sha256': digest(content)})
            except (ValueError, OSError):
                skipped.append({'path': rel, 'reason': 'unreadable, linked, special or oversized source'})
        if entries > entry_limit:
            return files, skipped, True
    return files, skipped, False


def location(root, row, patterns):
    path, start, end = row['file'], row['lineStart'], row['lineEnd']
    relative, content = local_file(root, path, patterns)
    if start is None and end is None:
        pass
    elif (type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(content.splitlines())):
        raise ValueError('source line range is not present in current target')
    return {'file': relative, 'lineStart': start, 'lineEnd': end}, digest(content)


def tool_rows(tool, report):
    if tool == 'semgrep':
        if not isinstance(report, dict) or not isinstance(report.get('results'), list):
            raise ValueError('unsupported Semgrep report')
        if report.get('errors'):
            raise ValueError('Semgrep report contains execution errors')
        for row in report['results']:
            extra = row.get('extra', {})
            yield {'external': row['check_id'], 'category': 'source-security',
                   'severity': {'ERROR': 'High', 'WARNING': 'Medium', 'INFO': 'Informational'}.get(extra.get('severity'), 'Medium'),
                   'location': {'file': row['path'], 'lineStart': row['start']['line'], 'lineEnd': row['end']['line']}}
    elif tool == 'gitleaks':
        if not isinstance(report, list):
            raise ValueError('unsupported Gitleaks report')
        for row in report:
            yield {'external': row['RuleID'], 'category': 'secrets', 'severity': 'High',
                   'location': {'file': row['File'], 'lineStart': row['StartLine'], 'lineEnd': row['EndLine']}}
    elif tool == 'panda-security':
        if not isinstance(report, dict) or report.get('schemaVersion') != 'panda-security.findings/v1':
            raise ValueError('unsupported Security report')
        for row in report['findings']:
            for loc in row['locations']:
                yield {'external': row['ruleId'] or row['category'], 'category': row['category'],
                       'severity': row['severity'], 'id': row['id'], 'security': row,
                       'location': {'file': loc['path'], 'lineStart': loc['lineStart'], 'lineEnd': loc['lineEnd']}}
    else:
        raise ValueError('unsupported import format')


def build(target, sources, options, api, secrets=()):
    secrets = list(secrets)
    target = Path(target)
    if target.is_symlink() or not target.is_dir():
        raise ValueError('scan target must be an existing non-linked directory')
    target = target.resolve()
    now = datetime.now(timezone.utc).isoformat()
    scan_id = 'SCAN-' + uuid.uuid4().hex[:12]
    case = {'schemaVersion': 'panda-case.case/v1', 'id': scan_id, 'title': 'Local scan evidence',
            'mode': 'scan', 'state': 'scoped', 'incidentClassification': 'Inconclusive', 'engagementId': 'LOCAL-OFFLINE',
            'assets': [], 'evidence': [], 'findings': [], 'observations': [],
            'limitations': ['Imported findings require human source/control review; no scanner or security test was executed by this helper.'],
            'history': [{'from': None, 'to': 'created', 'reason': 'Create offline scan record', 'at': now},
                        {'from': 'created', 'to': 'scoped', 'reason': 'Explicit local target and exclusions only', 'at': now}]}
    files, skipped, truncated = discover(target, options.depth, options.exclude)
    metadata = {'schemaVersion': 'panda-red.scan-metadata/v1', 'scanId': scan_id, 'timestamp': now,
                'revision': None, 'depth': options.depth, 'offline': True, 'noTools': options.no_tools,
                'assessmentBy': 'normalizer', 'assessmentStatus': 'Partial', 'processingStatus': 'Completed', 'toolsExecuted': [],
                'imports': [], 'files': files, 'excludedOrUnreadable': skipped, 'discoveryTruncated': truncated,
                'findingCount': 0, 'duplicatesMerged': 0,
                'limitations': ['Local inventory and supplied-result normalization only; manual analysis/coverage remains unverified.',
                                'No current dependency advisory lookup or runtime validation was performed.',
                                'Trusted-root, non-concurrent filesystem assumptions apply; this helper is not a sandbox.']}
    metadata['toolsConsidered'] = [{'tool': tool, 'availability': 'Available' if shutil.which(tool) else 'Missing',
                                   'version': None, 'executionStatus': 'Not Run',
                                   'reason': 'No-tools request or import-only helper; never automatically launched.'}
                                  for tool in ('semgrep', 'gitleaks', 'trivy', 'osv-scanner', 'govulncheck', 'cargo-audit', 'npm', 'pip-audit')]
    if len(sources) > 16:
        raise ValueError('report input count limit exceeded')
    groups, assets, seen_reports = {}, {}, set()
    for tool, path in sources:
        snapshot = copy.deepcopy((case, groups, assets, metadata['duplicatesMerged']))
        record = {'tool': tool, 'status': 'Imported', 'helperExecuted': False, 'sourceExitCode': None,
                  'reportSha256': None, 'reason': 'Supplied local report; producer execution is not verified.'}
        try:
            report, raw = api['load_json'](path, with_bytes=True)
            report_hash = digest(raw)
            record['reportSha256'] = report_hash
            if (tool, report_hash) in seen_reports:
                record['reason'] = 'Identical report already imported; no duplicate findings added.'
                metadata['imports'].append(record)
                continue
            rows = list(tool_rows(tool, report))
            if len(rows) > 1000:
                raise ValueError('finding limit exceeded')
            # Validate an entire input before merging so malformed reports cannot half-import.
            checked = [(row, *location(target, row['location'], options.exclude)) for row in rows]
            report_secrets = list(secrets)
            if tool == 'gitleaks':
                report_secrets.extend(row.get('Secret', '') for row in report if isinstance(row.get('Secret', ''), str))
                secrets.extend(report_secrets)
            report_evidence = 'E-' + report_hash[:16]
            if not any(e['id'] == report_evidence for e in case['evidence']):
                case['evidence'].append({'schemaVersion': 'panda-case.evidence/v1', 'id': report_evidence,
                    'caseId': scan_id, 'source': 'Imported local scanner/analyst report', 'collectedAt': now,
                    'sourceTimestamp': None, 'sourceTimezone': None, 'artifact': None, 'sha256': report_hash,
                    'method': 'Local import; hash identifies supplied bytes, not authenticity or executed scanning',
                    'relatedFindings': [], 'sensitivity': 'Restricted', 'redactionStatus': 'Sanitized', 'integrity': 'Unchecked'})
            for row, loc, source_hash in checked:
                if row['severity'] not in SEVERITIES:
                    raise ValueError('unsupported severity')
                key = (row.get('id') or str(row['external']), loc['file'], loc['lineStart'], loc['lineEnd'])
                fingerprint = digest(json.dumps(key, separators=(',', ':')).encode())
                identity = row.get('id') or 'F-' + fingerprint[:16]
                if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', identity) or scrub(identity, report_secrets) != identity:
                    raise ValueError('unsafe finding identifier')
                # Security rows keep their root-cause ID across locations; scanner matches need manual cross-rule dedup.
                group = identity
                provenance = {'tool': tool, 'reportSha256': report_hash, 'originFingerprint': fingerprint, 'helperExecuted': False}
                if group in groups:
                    finding = groups[group]
                    if finding['severity'] != row['severity']:
                        raise ValueError('conflicting imported severities require manual reconciliation')
                    if loc not in finding['locations']: finding['locations'].append(loc)
                    if report_evidence not in finding['evidenceRefs']: finding['evidenceRefs'].append(report_evidence)
                    if provenance not in finding['provenance']: finding['provenance'].append(provenance)
                    metadata['duplicatesMerged'] += 1
                    continue
                if loc['file'] not in assets:
                    aid = 'A-' + digest(loc['file'].encode())[:16]
                    assets[loc['file']] = aid
                    case['assets'].append({'schemaVersion': 'panda-case.asset/v1', 'id': aid, 'caseId': scan_id,
                        'type': 'application', 'locator': loc['file'], 'scope': 'In scope', 'exposure': 'Configured',
                        'observedAt': now, 'confidence': 'Confirmed', 'evidenceRefs': [report_evidence]})
                security = row.get('security')
                status = 'Potential concern'
                if security:
                    if security['classification'] not in {'Confirmed vulnerability', 'Likely vulnerability', 'False positive', 'Hardening', 'Informational'}:
                        raise ValueError('unsupported Security classification')
                    status = {'Confirmed vulnerability': 'Confirmed vulnerability', 'Likely vulnerability': 'Requires verification',
                              'False positive': 'False positive'}.get(security['classification'], 'Potential concern')
                vulnerability = ('Verified vulnerability' if status == 'Confirmed vulnerability' else
                                 'False positive' if status == 'False positive' else
                                 'Informational' if security and security['classification'] in {'Hardening', 'Informational'} else
                                 'Potential weakness')
                finding = {'schemaVersion': 'panda-case.finding/v1', 'id': identity, 'caseId': scan_id,
                    'title': security['title'] if security else ('Potential credential exposure' if tool == 'gitleaks' else 'Static scanner concern requiring review'),
                    'category': row['category'], 'assetId': assets[loc['file']], 'severity': row['severity'],
                    'severityRationale': security['severityRationale'] if security else 'Upstream rule priority only; contextual impact requires manual assessment.',
                    'confidence': security['confidence'] if security else 'Unknown',
                    'vulnerabilityStatus': vulnerability,
                    'verificationStatus': 'Source traced' if security and security['verification']['status'] == 'source-traced' else 'Not tested',
                    'preconditions': security['attackerPrerequisites'] if security else 'Unverified; trace attacker control and effective guards.',
                    'invariant': 'Only authorized input and identities may cross the identified security boundary.',
                    'observedBehavior': 'Imported claim located in current source; source SHA-256 ' + source_hash + '. No exploit was executed.',
                    'expectedBehavior': 'Preserve the applicable input, access and data-protection boundary.',
                    'evidenceRefs': [report_evidence], 'reproduction': 'Review current source and relevant unchanged guards; no payload executed by helper.',
                    'rootCause': None, 'impact': security['impact'] if security else 'Not established from a scanner match alone.',
                    'remediation': security['remediation'] if security else 'Confirm the causal path and controls before selecting remediation.',
                    'regression': security['regression'] if security else 'Use a safe negative/control pair against the verified invariant; not run.',
                    'controlsConsidered': security['controlsConsidered'] if security else 'Not yet assessed; trace relevant guards and caller controls before confirmation.',
                    'mappings': [], 'sourceMode': 'scan', 'status': status, 'locations': [loc], 'provenance': [provenance], 'aliases': []}
                finding = scrub(finding, report_secrets)
                api['validate']('finding', finding)
                if len(case['findings']) >= 1000:
                    raise ValueError('canonical finding limit exceeded')
                groups[group] = finding
                case['findings'].append(finding)
            seen_reports.add((tool, report_hash))
        except (ValueError, OSError, KeyError, TypeError, AttributeError):
            case, groups, assets, metadata['duplicatesMerged'] = snapshot
            record['status'], record['reason'] = 'Refused', 'Malformed, inaccessible, conflicting, out-of-scope or unsupported report; no clean scan conclusion.'
            metadata['processingStatus'] = 'Partial'
        metadata['imports'].append(record)
    if not sources:
        metadata['limitations'].append('No scanner/analyst results supplied; zero findings is not a clean assessment.')
    metadata['findingCount'] = len(case['findings'])
    for evidence in case['evidence']:
        evidence['relatedFindings'] = [f['id'] for f in case['findings'] if evidence['id'] in f['evidenceRefs']]
    case, metadata = scrub(case, secrets), scrub(metadata, secrets)
    api['validate']('case', case)
    api['validate']('scan-metadata', metadata)
    return case, metadata


def correlate(case, mappings, api):
    """Apply explicit reviewed root-cause groups; never infer equivalence by proximity."""
    if not isinstance(mappings, list) or len(mappings) > 1000:
        raise ValueError('invalid correlation mapping')
    case = copy.deepcopy(case)
    findings = {f['id']: f for f in case['findings']}
    primaries, removed = set(), set()
    for group in mappings:
        if (not isinstance(group, dict) or set(group) != {'primaryId', 'duplicates', 'reason'}
                or not isinstance(group['duplicates'], list) or not group['duplicates']
                or not isinstance(group['reason'], str) or not group['reason'].strip()):
            raise ValueError('correlation needs explicit IDs and reviewed reason')
        primary, duplicates = group['primaryId'], group['duplicates']
        if (primary not in findings or primary in primaries or len(set(duplicates)) != len(duplicates)
                or any(d not in findings or d == primary or d in removed for d in duplicates)):
            raise ValueError('unknown or repeated correlation ID')
        primaries.add(primary); removed.update(duplicates)
    if primaries & removed:
        raise ValueError('cyclic correlation mapping')
    for group in mappings:
        primary = findings[group['primaryId']]
        for duplicate in group['duplicates']:
            row = findings[duplicate]
            for key in ('locations', 'evidenceRefs', 'provenance'):
                for value in row[key]:
                    if value not in primary[key]: primary[key].append(value)
            primary['aliases'] = sorted(set(primary['aliases'] + [duplicate] + row['aliases']))
            # Preserve differing producer assessments as evidence, not a severity upgrade.
            primary.setdefault('correlationNotes', []).append(
                duplicate + ': original ' + row['severity'] + '/' + row['confidence'] + '/' + row['status'])
            for evidence in case['evidence']:
                if duplicate in evidence['relatedFindings']:
                    evidence['relatedFindings'] = sorted(set(group['primaryId'] if x == duplicate else x for x in evidence['relatedFindings']))
    case['findings'] = [row for row in case['findings'] if row['id'] not in removed]
    return api['validate']('case', case)


def markdown(case, metadata, minimum):
    def text(value):
        escaped = html.escape(str(value), quote=False).replace('\n', ' / ')
        return re.sub(r'([\\`*_{}\[\]()#+!|>])', r'\\\1', escaped)
    visible = [f for f in case['findings'] if SEVERITIES.index(f['severity']) >= SEVERITIES.index(minimum)]
    lines = ['# Security scan', '', '## Executive summary', '',
             f'Assessment: {metadata["assessmentStatus"]}. {len(case["findings"])} canonical findings; {len(visible)} displayed.',
             'Zero findings is not proof of security.', '', '## Scope and environment', '',
             f'Bounded local target; {len(metadata["files"])} files inventoried. No target or advisory service contacted.',
             '', '## Scan methodology', '', f'Depth: {metadata["depth"]}. Supplied findings normalized; manual causal review remains necessary.',
             '', '## Tools executed', '', 'None by this helper. Imported producer claims are not helper-executed scans.',
             '', '## Findings by severity', '']
    for severity in reversed(SEVERITIES):
        lines.append(f'- {severity}: {sum(f["severity"] == severity for f in case["findings"])} canonical.')
    lines += ['', '## Detailed findings', '']
    for finding in visible:
        lines += ['### ' + text(finding['id']) + ' — ' + text(finding['title']), '',
                  f'{finding["severity"]}; {finding["confidence"]}; {finding["status"]}; category: {text(finding["category"])}.']
        for loc in finding['locations']:
            lines.append(f'- Location: {text(loc["file"])}; lines {loc["lineStart"]}–{loc["lineEnd"]} (null means unavailable).')
        lines += ['- Evidence IDs: ' + ', '.join(text(e) for e in finding['evidenceRefs']),
                  '- Impact: ' + text(finding['impact']), '- Recommendation: ' + text(finding['remediation']),
                  '- Controls considered: ' + text(finding['controlsConsidered']),
                  '- Verification: ' + text(finding['verificationStatus']), '']
        if finding['aliases']:
            lines.append('- Correlated IDs: ' + ', '.join(text(v) for v in finding['aliases']))
    lines += ['## Evidence and reproduction status', '',
              'Locations and ranges were checked against current source. Imported report execution and claims remain unverified.',
              '', '## Recommended remediation', '', 'Prioritize supported practical impact; manually reject false positives before changing source.',
              '', '## Suggested regression tests', '']
    lines += ['- ' + text(f['id']) + ': ' + text(f['regression']) for f in visible]
    lines += ['', '## Assessment limitations', ''] + ['- ' + text(v) for v in metadata['limitations']]
    lines += ['- Severity filtering affects this view only; findings.json retains every normalized finding.',
              '- Automatic masking is conservative; review narrative/paths for unrecognized sensitive data before sharing.', '']
    return '\n'.join(lines)


def write_bundle(case, metadata, output, minimum, format):
    output = Path(output).absolute()
    for parent in [output, *output.parents]:
        if parent.is_symlink():
            raise ValueError('linked report destination refused; use a canonical path')
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    output.mkdir(mode=0o700)  # Exclusive: no prior scan is overwritten.
    metadata = dict(metadata, viewMinimumSeverity=minimum, viewFormat=format, publicationStatus='Complete')
    contents = {'findings.json': json.dumps(case, indent=2, ensure_ascii=True) + '\n'}
    if format in ('markdown', 'both'):
        contents['SECURITY_SCAN.md'] = markdown(case, metadata, minimum)
    # Metadata is published last; a missing metadata record means incomplete publication.
    contents['scan-metadata.json'] = json.dumps(metadata, indent=2, ensure_ascii=True) + '\n'
    for name, content in contents.items():
        descriptor = os.open(output / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            stream.write(content)
    return {'scanId': case['id'], 'assessmentStatus': metadata['assessmentStatus'],
            'processingStatus': metadata['processingStatus'], 'findingCount': len(case['findings']),
            'displayedFindingCount': sum(SEVERITIES.index(f['severity']) >= SEVERITIES.index(minimum) for f in case['findings']),
            'files': list(contents), 'toolsExecuted': [], 'outputCreated': True}
