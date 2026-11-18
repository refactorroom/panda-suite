"""Agent request contracts. Validation/help only; never execute an agent mode."""

import argparse
from pathlib import Path

SEVERITIES = ['Informational', 'Low', 'Medium', 'High', 'Critical']


def severity(value):
    normalized = value.capitalize()
    if normalized not in SEVERITIES:
        raise argparse.ArgumentTypeError('severity must be informational, low, medium, high or critical')
    return normalized


def help_text(contract, mode=None):
    modes = {item['name']: item for item in contract['modes']}
    if mode is not None and mode not in modes:
        raise ValueError('unsupported mode; choose ' + ', '.join(modes))
    lines = ['Panda Blue ' + contract['skillVersion'] + ' — agent workflow help',
             'Agent: $panda-blue MODE TARGET (standalone Codex; host names differ).',
             'These cues do not execute a shell command or an installed agent automatically.']
    for name in ([mode] if mode else modes):
        entry = modes[name]
        lines += ['', name + ': ' + entry['purpose'], 'Input: ' + entry['input'], 'Outputs: ' + entry['outputs']]
    lines += ['', 'Helper: blue.py request MODE TARGET validates the request only.',
              'Installer: panda-suite install/update copies skills; npx skills is not mode execution.',
              'panda-blue never contacts assessment targets; scan, recon, simulate and bounty belong to panda-red.']
    if mode in (None, 'intel'):
        lines += ['', 'Intel: latest, update, status, owasp, cve CVE-ID, kev, incidents [--days N: default 1 for latest/update, 7 for incidents].',
                  'Helper intel requires --allow-network for live reads; --offline reads dated cache.',
                  'hunt/incident accept --intel off|cache|live; explicit --offline conflicts with live.',
                  'Package queries need separate --allow-package-queries; no scheduler is activated.']
    return '\n'.join(lines)


def parse_request(argv, contract):
    parser = argparse.ArgumentParser(prog='panda-blue request', description='Validate an agent request without executing it.')
    modes = parser.add_subparsers(dest='mode', required=True)
    for item in contract['modes']:
        command = modes.add_parser(item['name'], help=item['purpose'])
        if item['name'] == 'intel':
            command.add_argument('topic', choices=contract['intelTopics'])
            command.add_argument('identifier', nargs='?')
            command.add_argument('--days', type=int)
            command.add_argument('--ecosystem', choices=['go', 'npm', 'pypi'])
            command.add_argument('--severity', type=severity)
            command.add_argument('--offline', action='store_true')
            continue
        command.add_argument('target', type=Path, help=item['input'])
        if item['name'] in ('hunt', 'incident'):
            command.add_argument('--intel', choices=['off', 'cache', 'live'], default='off')
            command.add_argument('--offline', action='store_true')
    other = {'scan', 'recon', 'simulate', 'bounty'}
    if argv and argv[0] in other:
        raise ValueError('unsupported mode for panda-blue: ' + argv[0] + ' belongs to panda-red')
    args = parser.parse_args(argv)
    if args.mode == 'intel':
        import re
        days = args.days if args.days is not None else (7 if args.topic == 'incidents' else 1)
        if (not 1 <= days <= 120 or args.topic == 'cve' and not re.fullmatch(r'CVE-\d{4}-\d{4,19}', args.identifier or '')
                or args.topic != 'cve' and args.identifier is not None):
            raise ValueError('intel requires a valid topic/CVE and days 1–120')
        return {'schemaVersion': 'panda-blue.request/v1', 'mode': 'intel', 'topic': args.topic,
                'identifier': args.identifier, 'days': days, 'ecosystem': args.ecosystem,
                'severity': args.severity, 'offline': args.offline, 'executed': False,
                'permission': 'No execution; live public lookup intent does not authorize private package queries or probing'}
    path = args.target
    if path.is_symlink() or not path.exists() or not (path.is_file() or path.is_dir()):
        raise ValueError('invalid target: choose an existing authorized regular file or directory')
    result = {'schemaVersion': 'panda-blue.request/v1', 'mode': args.mode,
              'target': str(path.resolve()), 'executed': False, 'permission': 'local read-only request only'}
    if args.mode in ('hunt', 'incident'):
        if args.offline and args.intel == 'live': raise ValueError('intel live conflicts with explicit offline')
        result['options'] = {'intel': args.intel, 'offline': args.offline or args.intel != 'live',
                             'networkScope': 'public-intelligence-only' if args.intel == 'live' else 'none'}
    return result
