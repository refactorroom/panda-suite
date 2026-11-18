#!/usr/bin/env python3
"""panda-red offline record/scope utilities. No target connections, scanners or persistent store."""

import argparse
from datetime import datetime, timezone
from functools import lru_cache
import copy
import importlib.util
import ipaddress
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

BASE = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=8)
def support(name):
    if name not in {'case_core', 'commands', 'scan'}:
        raise ValueError('unknown bundled helper module')
    spec = importlib.util.spec_from_file_location('_panda_red_' + name, BASE / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_core = support('case_core')
MAX_JSON, MAX_ARTIFACT, MAX_TOTAL_ARTIFACT = _core.MAX_JSON, _core.MAX_ARTIFACT, _core.MAX_TOTAL_ARTIFACT
TRANSITIONS = _core.TRANSITIONS
pairs, invalid_constant, finite_float = _core.pairs, _core.invalid_constant, _core.finite_float
load_json, timestamp, validators, validate = _core.load_json, _core.timestamp, _core.validators, _core.validate
relative_path, check_integrity, transition, render = _core.relative_path, _core.check_integrity, _core.transition, _core.render


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



def engagement_check(data):
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


_core.CHECKS['engagement'] = engagement_check


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



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    command_api = support('commands')
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
    command.add_argument('kind', choices=['engagement', 'case', 'asset', 'finding', 'evidence', 'scan-metadata'])
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
        if args.action in {'help', 'request'}:
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
            output_path = args.output or Path('.panda-suite/red/reports/scans') / case['id']
            output = scanner.write_bundle(case, metadata, output_path, args.severity, args.format)
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
