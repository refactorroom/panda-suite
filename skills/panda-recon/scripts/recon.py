#!/usr/bin/env python3
"""Offline record/scope utilities. No target connections, scanners or persistent store."""

import argparse
import copy
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import importlib.util
import ipaddress
import json
import math
from pathlib import Path
import re
import stat
import sys
from urllib.parse import urlsplit

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


@lru_cache(maxsize=8)
def support(name):
    if name not in {'commands', 'scan', 'intel', 'intel_sources', 'intel_store', 'intel_net', 'components'}:
        raise ValueError('unknown bundled helper module')
    spec = importlib.util.spec_from_file_location('_panda_recon_' + name, BASE / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError('timestamp needs an explicit offset')
    return parsed


def target_url(value):
    # Conservative subset: no query, fragment, encodings, dot-segments or userinfo.
    if not isinstance(value, str) or not value.isascii() or re.search(r'[\s\\%?#]', value):
        raise ValueError('unsupported or ambiguous target URL')
    parsed = urlsplit(value)
    if parsed.scheme not in {'http', 'https'} or not parsed.netloc or parsed.username is not None:
        raise ValueError('unsupported target origin')
    host = parsed.hostname
    if not host or host.endswith('.'):
        raise ValueError('ambiguous host')
    try:
        host = str(ipaddress.ip_address(host))
    except ValueError:
        labels = host.split('.')
        if (host.isdigit() or host.startswith('0x') or all(p.isdigit() for p in labels)
                or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', p) for p in labels)):
            raise ValueError('unsupported host')
    port = parsed.port if parsed.port is not None else (443 if parsed.scheme == 'https' else 80)
    if not 1 <= port <= 65535 or parsed.netloc.endswith(':'):
        raise ValueError('invalid target port')
    path = parsed.path or '/'
    if (not re.fullmatch(r'/[A-Za-z0-9._~/-]*', path) or '//' in path
            or any(p in {'.', '..'} for p in path.split('/'))):
        raise ValueError('ambiguous target path')
    return parsed.scheme, host, port, path


def path_matches(candidate, rule):
    prefix = rule[3].rstrip('/')
    return candidate[:3] == rule[:3] and (not prefix or candidate[3] == prefix or candidate[3].startswith(prefix + '/'))


def network(value):
    return ipaddress.ip_network(value, strict=True)


@lru_cache(maxsize=1)
def validators():
    try:
        import jsonschema
        from referencing import Registry, Resource
    except ImportError as error:
        raise ValueError('optional helper requires jsonschema; use an existing configured environment') from error
    resources = [(schema['$id'], Resource.from_contents(schema))
                 for schema in (load_json(p) for p in sorted((BASE / 'schemas').glob('*.schema.json')))]
    schemas = dict((uri, resource.contents) for uri, resource in resources)
    registry = Registry().with_resources(resources)
    return {kind: jsonschema.Draft202012Validator(
        schemas['urn:panda-recon:' + kind + ':v1'], registry=registry,
        format_checker=jsonschema.FormatChecker())
        for kind in ('engagement', 'case', 'asset', 'finding', 'evidence', 'scan-metadata', 'intelligence')}


def validate(kind, data):
    if kind not in {'engagement', 'case', 'asset', 'finding', 'evidence', 'scan-metadata', 'intelligence'}:
        raise ValueError('unknown record kind')
    checker = validators()[kind]
    if next(checker.iter_errors(data), None) is not None:
        raise ValueError('record does not match its local schema')
    if kind == 'engagement':
        for rule in data['scope']['targets']:
            origin = target_url(rule['url'])
            nets = [network(v) for v in rule['allowedAddresses']]
            try:
                literal = ipaddress.ip_address(origin[1])
            except ValueError:
                literal = None
            if literal is not None and nets and not any(literal in n for n in nets):
                raise ValueError('literal target is outside its address allowlist')
        for value in data['scope']['exclusions']:
            target_url(value)
        for value in data['scope']['excludedAddresses']:
            network(value)
        auth, testing = data['authorization'], data['testing']
        if (type(testing['maxRequestsPerSecond']) is float
                and not math.isfinite(testing['maxRequestsPerSecond'])):
            raise ValueError('invalid rate limit')
        if data['environment'] == 'offline' and testing['activeAllowed']:
            raise ValueError('offline environment cannot declare active work')
        if auth['validFrom'] and auth['validUntil'] and timestamp(auth['validFrom']) >= timestamp(auth['validUntil']):
            raise ValueError('invalid authorization window')
        if testing['activeAllowed'] and (auth['status'] != 'approved' or not auth['evidenceReference']
                or not auth['validFrom'] or not auth['validUntil'] or not testing['techniques']
                or testing['maxTotalRequests'] < 1
                or any(not r['allowedAddresses'] for r in data['scope']['targets'])):
            raise ValueError('active declaration lacks explicit constraints')
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


def scope_check(engagement, url, resolutions, redirects, technique, at,
                requests_used=0, elapsed_seconds=0, current_rate=0):
    validate('engagement', engagement)
    auth, testing = engagement['authorization'], engagement['testing']
    if any(type(n) not in {int, float} or (type(n) is float and not math.isfinite(n)) or n < 0
           for n in (requests_used, elapsed_seconds, current_rate)):
        raise ValueError('invalid budget observation')
    if type(requests_used) is not int:
        raise ValueError('request count must be an integer')
    reason = None
    if not testing['activeAllowed'] or auth['status'] != 'approved' or not auth['evidenceReference']:
        reason = 'active activity is not declared approved'
    elif not timestamp(auth['validFrom']) <= timestamp(at) < timestamp(auth['validUntil']):
        reason = 'outside authorization window'
    elif technique not in testing['techniques']:
        reason = 'technique not listed'
    elif (requests_used >= testing['maxTotalRequests'] or elapsed_seconds >= testing['maxDurationSeconds']
          or current_rate > testing['maxRequestsPerSecond']):
        reason = 'engagement budget exhausted'
    else:
        try:
            if not isinstance(resolutions, dict) or not isinstance(redirects, list):
                raise ValueError('invalid supplied resolution or redirect data')
            exclusions = [target_url(v) for v in engagement['scope']['exclusions']]
            excluded_ips = [network(v) for v in engagement['scope']['excludedAddresses']]
            if len(redirects) > 10:
                raise ValueError('redirect limit exceeded')
            for value in [url, *redirects]:
                target = target_url(value)
                if any(path_matches(target, rule) for rule in exclusions):
                    raise ValueError('excluded target')
                rules = [r for r in engagement['scope']['targets'] if path_matches(target, target_url(r['url']))]
                if not rules:
                    raise ValueError('target outside declared scope')
                raw = resolutions.get(target[1])
                if (not isinstance(raw, list) or not 1 <= len(raw) <= 1000
                        or not all(isinstance(value, str) for value in raw)):
                    raise ValueError('missing supplied DNS/address evidence')
                addresses = [ipaddress.ip_address(v) for v in raw]
                try:
                    literal = ipaddress.ip_address(target[1])
                except ValueError:
                    literal = None
                if literal is not None and set(addresses) != {literal}:
                    raise ValueError('literal target address mismatch')
                if any(any(ip in n for n in excluded_ips) for ip in addresses):
                    raise ValueError('excluded address')
                if not any(all(any(ip in network(n) for n in r['allowedAddresses']) for ip in addresses) for r in rules):
                    raise ValueError('resolved address outside declared scope')
        except (ValueError, TypeError, AttributeError):
            reason = 'target, redirect or supplied address evidence is outside supported scope'
    return {'scopeEligible': reason is None, 'reason': reason or 'all supplied scope constraints matched',
            'operatorAuthority': 'not verified by this helper', 'targetContacted': False,
            'limitation': 'Offline preflight only; no DNS rebinding, live budgets or authorization enforcement.'}


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


def inventory(engagement, assets):
    validate('engagement', engagement)
    if not engagement['testing']['passiveAllowed']:
        raise ValueError('passive collection not permitted by declaration')
    if not isinstance(assets, list) or len(assets) > 1000:
        raise ValueError('invalid inventory or record limit')
    if len({a.get('id') for a in assets if isinstance(a, dict)}) != len(assets):
        raise ValueError('duplicate or malformed inventory records')
    output = []
    for asset in assets:
        validate('asset', asset)
        row = copy.deepcopy(asset)
        try:
            target = target_url(asset['locator'])
            excluded = any(path_matches(target, target_url(r)) for r in engagement['scope']['exclusions'])
            included = any(path_matches(target, target_url(r['url'])) for r in engagement['scope']['targets'])
            row['scope'] = 'Excluded' if excluded else ('In scope' if included else 'Unverified')
        except ValueError:
            row['scope'] = 'Unverified'
        output.append(row)
    return {'engagementId': engagement['id'], 'assets': output,
            'limitation': 'Supplied inventory only; declared scope is not authority or observed reachability.'}


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    command_api = support('commands')
    command = commands.add_parser('intel', help='on-demand public intelligence; network requires explicit opt-in')
    command.add_argument('intel_args', nargs=argparse.REMAINDER)
    command = commands.add_parser('help', help='explain agent modes without executing them')
    command.add_argument('mode', nargs='?')
    command = commands.add_parser('request', help='validate an agent mode request, without executing it')
    command.add_argument('request_args', nargs=argparse.REMAINDER)
    command = commands.add_parser('scan-report', help='normalize supplied local reports; never launch scanners')
    command.add_argument('target', type=Path)
    command_api.options(command)
    command.add_argument('--security-report', type=Path, action='append', default=[])
    command.add_argument('--semgrep-report', type=Path, action='append', default=[])
    command.add_argument('--gitleaks-report', type=Path, action='append', default=[])
    command.add_argument('--redactions', type=Path, help='private JSON array of exact values to mask; never put secrets in CLI arguments')
    command.add_argument('--correlations', type=Path, help='explicit reviewed primary/duplicate ID groups; no automatic cross-rule inference')
    command = commands.add_parser('validate')
    command.add_argument('kind', choices=['engagement', 'case', 'asset', 'finding', 'evidence', 'scan-metadata', 'intelligence'])
    command.add_argument('file', type=Path)
    for action in ('integrity', 'render', 'transition'):
        command = commands.add_parser(action)
        command.add_argument('file', type=Path)
        if action == 'integrity':
            command.add_argument('--root', type=Path, required=True)
        if action == 'transition':
            command.add_argument('--to', required=True)
            command.add_argument('--reason', required=True)
            command.add_argument('--at', required=True)
    command = commands.add_parser('inventory')
    command.add_argument('engagement', type=Path)
    command.add_argument('assets', type=Path, help='JSON array of supplied asset records')
    command = commands.add_parser('scope')
    command.add_argument('engagement', type=Path)
    command.add_argument('url')
    command.add_argument('--resolutions', type=Path, required=True, help='supplied host to IP-array JSON; no DNS query')
    command.add_argument('--redirects', type=Path, help='supplied JSON array; no redirect followed')
    command.add_argument('--technique', required=True)
    command.add_argument('--at', default=datetime.now(timezone.utc).isoformat())
    command.add_argument('--requests-used', type=int, default=0)
    command.add_argument('--elapsed-seconds', type=float, default=0)
    command.add_argument('--current-rate', type=float, default=0)
    args = parser.parse_args()
    try:
        code = 0
        if args.action == 'intel':
            intelligence = support('intel')
            intel_args = intelligence.parser().parse_args(args.intel_args)
            output = intelligence.run(intel_args, globals())
            validate('intelligence', output)
            code = 3 if any(s['status'] in ('Stale', 'Unavailable') or s.get('lastAttemptError') for s in output['sourceStatus'] if s.get('enabled', True)) else 0
            if intel_args.output:
                output = intelligence.write(output, intel_args.output)
        elif args.action in {'help', 'request'}:
            contract = load_json(BASE / 'assets/command-contract.json')
            if args.action == 'help':
                print(command_api.help_text(contract, args.mode))
                return 0
            output = command_api.parse_request(args.request_args, contract)
        elif args.action == 'scan-report':
            scanner = support('scan')
            sources = [('panda-security', p) for p in args.security_report]
            sources += [('semgrep', p) for p in args.semgrep_report]
            sources += [('gitleaks', p) for p in args.gitleaks_report]
            secrets = load_json(args.redactions) if args.redactions else []
            if not isinstance(secrets, list) or any(not isinstance(s, str) or len(s) < 4 for s in secrets):
                raise ValueError('redactions must be an array of values at least four characters long')
            case, metadata = scanner.build(args.target, sources, args, globals(), secrets)
            if args.correlations:
                before = len(case['findings'])
                case = scanner.correlate(case, load_json(args.correlations), globals())
                metadata['correlationsApplied'] = before - len(case['findings'])
                metadata['findingCount'] = len(case['findings'])
            intel_data = None
            if args.intel != 'off':
                if args.intel == 'live' and args.offline:
                    raise ValueError('live intelligence conflicts with explicit offline')
                intelligence = support('intel')
                flags = ['latest', '--cache', str(args.intel_cache)]
                if args.intel == 'cache': flags.append('--offline')
                if args.allow_network: flags.append('--allow-network')
                if args.allow_package_queries: flags.append('--allow-package-queries')
                if args.components: flags += ['--components', str(args.components)]
                else: flags += ['--project', str(args.target)]
                intel_data = intelligence.run(intelligence.parser().parse_args(flags), globals())
                validate('intelligence', intel_data)
                metadata['intelligence'] = {'mode': args.intel, 'recordCount': len(intel_data['records']),
                    'exposureCount': len(intel_data['projectExposure']), 'caseClassificationChanged': False}
                if any(s['status'] in ('Stale', 'Unavailable') or s.get('lastAttemptError')
                       for s in intel_data['sourceStatus'] if s.get('enabled', True)):
                    metadata['processingStatus'] = 'Partial'
            output_path = args.output or Path('.panda-suite/recon/reports/scans') / case['id']
            output = scanner.write_bundle(case, metadata, output_path, args.severity, args.format)
            if intel_data is not None:
                output['intelligence'] = intelligence.write(intel_data, output_path / 'intelligence')
            code = 3 if metadata['processingStatus'] == 'Partial' else 0
        elif args.action == 'validate':
            validate(args.kind, load_json(args.file))
            output = {'valid': True, 'kind': args.kind}
        elif args.action == 'render':
            print(render(load_json(args.file)))
            return 0
        elif args.action == 'integrity':
            output = check_integrity(load_json(args.file), args.root)
            code = 0 if output and all(r['integrity'] == 'Matched' for r in output) else 2
        elif args.action == 'transition':
            output = transition(load_json(args.file), args.to, args.reason, args.at)
        elif args.action == 'inventory':
            output = inventory(load_json(args.engagement), load_json(args.assets))
        else:
            output = scope_check(load_json(args.engagement), args.url, load_json(args.resolutions),
                                 load_json(args.redirects) if args.redirects else [], args.technique, args.at,
                                 args.requests_used, args.elapsed_seconds, args.current_rate)
            code = 0 if output['scopeEligible'] else 2
        print(json.dumps(output, indent=2, ensure_ascii=True, allow_nan=False))
        return code
    except (ValueError, OSError, TypeError, KeyError, RecursionError) as error:
        # Never echo a raw invalid document, secret, path or imported exception detail.
        if args.action in {'help', 'request'} and isinstance(error, ValueError):
            print(str(error) + '. Use help or help MODE; no workflow was executed.', file=sys.stderr)
        else:
            category = ('PERMISSION_DENIED' if isinstance(error, PermissionError) else
                        'OUTPUT_EXISTS' if isinstance(error, FileExistsError) else
                        'INVALID_PATH' if isinstance(error, FileNotFoundError) else 'INVALID_INPUT_OR_SCOPE')
            print('Offline helper refused input or could not access required local data/dependencies. '
                  + category + ': check input schemas, target scope, report paths and existing output directories.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
