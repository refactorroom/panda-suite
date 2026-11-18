"""Shared case, evidence and record helpers for panda-red and panda-blue.

This file is kept byte-identical in both skills so each one stays standalone.
Edit both copies together; a test fails when they differ. Skill-specific record
checks register in CHECKS. No target connections, scanners or persistent store.
"""

import copy
from datetime import datetime
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import stat

BASE = Path(__file__).resolve().parents[1]
MAX_JSON = 1024 * 1024
MAX_ARTIFACT = 10 * 1024 * 1024
MAX_TOTAL_ARTIFACT = 50 * 1024 * 1024
TRANSITIONS = {
    'created': {'scoped', 'blocked'}, 'scoped': {'collecting', 'blocked'},
    'collecting': {'analyzing', 'blocked'}, 'analyzing': {'validating', 'reviewed', 'blocked'},
    'validating': {'analyzing', 'reviewed', 'blocked'},
    'reviewed': {'analyzing', 'reported', 'blocked'},
    'reported': {'analyzing', 'closed', 'blocked'},
    'blocked': {'scoped', 'collecting', 'analyzing', 'validating'}, 'closed': set(),
}
# Skill-specific semantic checks by record kind, e.g. CHECKS['engagement'] in panda-red.
CHECKS = {}


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError('non-finite JSON number')


def finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError('non-finite JSON number')
    return number


def load_json(path, with_bytes=False):
    path = Path(path)
    info = path.lstat()
    if path.is_symlink() or not stat.S_ISREG(info.st_mode) or info.st_size > MAX_JSON:
        raise ValueError('unsupported JSON input file')
    with path.open('rb') as stream:
        data = stream.read(MAX_JSON + 1)
    if len(data) > MAX_JSON:
        raise ValueError('JSON size limit exceeded')
    value = json.loads(data.decode('utf-8'), object_pairs_hook=pairs,
                       parse_constant=invalid_constant, parse_float=finite_float)
    return (value, data) if with_bytes else value


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError('timestamp needs an explicit offset')
    return parsed


@lru_cache(maxsize=1)
def validators():
    try:
        import jsonschema
        from referencing import Registry, Resource
    except ImportError as error:
        raise ValueError('optional helper requires jsonschema; use an existing configured environment') from error
    resources = [(schema['$id'], Resource.from_contents(schema))
                 for schema in (load_json(p) for p in sorted((BASE / 'schemas').glob('*.schema.json')))]
    registry = Registry().with_resources(resources)
    # Each bundled schema has an $id of the form urn:<namespace>:<kind>:v1.
    return {uri.split(':')[2]: jsonschema.Draft202012Validator(
        resource.contents, registry=registry, format_checker=jsonschema.FormatChecker())
        for uri, resource in resources}


def validate(kind, data):
    checkers = validators()
    if kind not in checkers:
        raise ValueError('unknown record kind')
    checker = checkers[kind]
    if next(checker.iter_errors(data), None) is not None:
        raise ValueError('record does not match its local schema')
    if kind in CHECKS:
        CHECKS[kind](data)
    elif kind == 'evidence':
        if data['artifact'] is not None:
            relative_path(data['artifact'])
        if data['integrity'] == 'Matched' and (not data['artifact'] or not data['sha256']):
            raise ValueError('matched evidence needs an artifact and hash')
    elif kind == 'finding':
        for location in data.get('locations', []):
            relative_path(location['file'])
            start, end = location['lineStart'], location['lineEnd']
            if (start is None) != (end is None) or (start is not None and start > end):
                raise ValueError('invalid finding line range')
    elif kind == 'case':
        ids = {}
        for group in ('assets', 'evidence', 'findings'):
            records = data[group]
            values = [r['id'] for r in records]
            if len(set(values)) != len(values):
                raise ValueError('duplicate record ID')
            ids[group] = set(values)
            for record in records:
                validate({'assets': 'asset', 'evidence': 'evidence', 'findings': 'finding'}[group], record)
                if record['caseId'] != data['id']:
                    raise ValueError('record belongs to a different case')
        for record in data['assets'] + data['findings']:
            if not set(record['evidenceRefs']) <= ids['evidence']:
                raise ValueError('dangling evidence reference')
        for finding in data['findings']:
            if finding['assetId'] not in ids['assets']:
                raise ValueError('dangling asset reference')
        for evidence in data['evidence']:
            if not set(evidence['relatedFindings']) <= ids['findings']:
                raise ValueError('dangling finding reference')
        if data['mode'] == 'simulate' and data['incidentClassification'] != 'Simulation only':
            raise ValueError('a simulation is not a real incident')
        state, prior = None, None
        for event in data['history']:
            at = timestamp(event['at'])
            if not event['reason'].strip():
                raise ValueError('case transition needs a reason')
            if event['from'] != state or (prior is not None and at < prior):
                raise ValueError('discontinuous case history')
            if state is None:
                if event['to'] != 'created':
                    raise ValueError('case history must start at created')
            elif event['to'] not in TRANSITIONS[state]:
                raise ValueError('invalid case transition')
            state, prior = event['to'], at
        if state != data['state']:
            raise ValueError('case state differs from history')
    return data


def relative_path(value):
    if (not isinstance(value, str) or not value or '\\' in value or ':' in value or '\x00' in value
            or any(part in {'', '.', '..'} for part in value.split('/')) or Path(value).is_absolute()):
        raise ValueError('unsafe artifact path')
    return Path(value)


def check_integrity(case, root):
    validate('case', case)
    root = Path(root).resolve(strict=True)
    results = []
    total = 0
    for item in case['evidence']:
        status = 'Unavailable'
        if item['artifact'] and item['sha256']:
            try:
                path = root
                for part in relative_path(item['artifact']).parts:
                    path = path / part
                    if path.is_symlink():
                        raise ValueError('linked evidence')
                if not path.resolve(strict=True).is_relative_to(root):
                    raise ValueError('evidence escapes root')
                info = path.stat()
                if (not stat.S_ISREG(info.st_mode) or info.st_size > MAX_ARTIFACT
                        or total + info.st_size > MAX_TOTAL_ARTIFACT):
                    raise ValueError('unsupported evidence file')
                with path.open('rb') as stream:
                    content = stream.read(MAX_ARTIFACT + 1)
                if len(content) > MAX_ARTIFACT:
                    raise ValueError('evidence size limit')
                total += len(content)
                status = 'Matched' if hashlib.sha256(content).hexdigest() == item['sha256'] else 'Mismatch'
            except (OSError, ValueError):
                status = 'Unavailable'
        results.append({'evidenceIndex': len(results), 'integrity': status})
    return results


def transition(case, state, reason, at):
    validate('case', case)
    if not isinstance(reason, str) or not reason.strip() or state not in TRANSITIONS[case['state']]:
        raise ValueError('transition needs an allowed destination and reason')
    result = copy.deepcopy(case)
    result['history'].append({'from': case['state'], 'to': state, 'reason': reason, 'at': at})
    result['state'] = state
    return validate('case', result)


def render(case):
    validate('case', case)
    # Only enums, indexes and counts are rendered. Arbitrary evidence/prose stays private.
    lines = ['# Case summary', '', 'Mode: ' + case['mode'], 'State: ' + case['state'],
             'Incident classification: ' + case['incidentClassification'], '', '## Assets', '']
    for i, asset in enumerate(case['assets']):
        lines.append(f'- assets[{i}]: {asset["type"]}; {asset["scope"]}; {asset["exposure"]}.')
    lines += ['', '## Findings', '']
    if not case['findings']:
        lines.append('No findings recorded; this is not proof of absence of vulnerabilities or incidents.')
    for i, finding in enumerate(case['findings']):
        ai = next(j for j, a in enumerate(case['assets']) if a['id'] == finding['assetId'])
        refs = [str(j) for j, e in enumerate(case['evidence']) if e['id'] in finding['evidenceRefs']]
        lines.append(f'- findings[{i}]: {finding["severity"]}; confidence {finding["confidence"]}; '
                     f'{finding["vulnerabilityStatus"]}; {finding["verificationStatus"]}; '
                     f'assets[{ai}]; evidence indexes: {", ".join(refs)}.')
    lines += ['', '## Evidence', '']
    for i, evidence in enumerate(case['evidence']):
        lines.append(f'- evidence[{i}]: {evidence["sensitivity"]}; {evidence["redactionStatus"]}; '
                     f'recorded integrity {evidence["integrity"]} (not rechecked by rendering).')
    lines += ['', '## Limits', '',
              f'{len(case["observations"])} observations and {len(case["limitations"])} limitations remain in the private JSON.',
              'This conservative view omits free text, identifiers, locators and raw artifacts. Indexes refer to the private case arrays.',
              'Use the analyst template for sanitized evidence, impact, remediation and reproducible steps.',
              'No network operation or security test was performed by rendering.', '']
    return '\n'.join(lines)
