"""Agent request contracts. Validation/help only; never execute an agent mode."""

import argparse
from pathlib import Path, PurePosixPath

SEVERITIES = ['Informational', 'Low', 'Medium', 'High', 'Critical']


def severity(value):
    normalized = value.capitalize()
    if normalized not in SEVERITIES:
        raise argparse.ArgumentTypeError('severity must be informational, low, medium, high or critical')
    return normalized


def exclusion(value):
    if (not value or '\\' in value or ':' in value or '\x00' in value
            or PurePosixPath(value).is_absolute() or '..' in value.split('/')):
        raise argparse.ArgumentTypeError('exclude must be a relative path or glob without traversal')
    return value


def options(parser):
    parser.add_argument('--depth', choices=['quick', 'deep'], default='quick')
    parser.add_argument('--severity', type=severity, default='Informational', help='minimum displayed severity; canonical JSON stays complete')
    parser.add_argument('--format', choices=['markdown', 'json', 'both'], default='both')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--exclude', action='append', type=exclusion, default=[])
    parser.add_argument('--offline', action='store_true', help='no remote operations; default unless intel live is explicitly selected')
    parser.add_argument('--no-tools', action='store_true', help='request manual/static work without launching external scanners')
    parser.add_argument('--intel', choices=['off', 'cache', 'live'], default='off')
    parser.add_argument('--intel-cache', type=Path, default=Path('.panda-suite/recon/intelligence-cache'))
    parser.add_argument('--components', type=Path)
    parser.add_argument('--allow-network', action='store_true', help='helper: permit fixed public intelligence requests only')
    parser.add_argument('--allow-package-queries', action='store_true', help='helper: permit sending exact package/version metadata to OSV')


def help_text(contract, mode=None):
    modes = {item['name']: item for item in contract['modes']}
    if mode is not None and mode not in modes:
        raise ValueError('unsupported mode; choose ' + ', '.join(modes))
    lines = ['Panda Recon ' + contract['skillVersion'] + ' — agent workflow help',
             'Agent: $panda-recon MODE TARGET (standalone Codex; host names differ).',
             'These cues do not execute a shell command or an installed agent automatically.']
    for name in ([mode] if mode else modes):
        entry = modes[name]
        lines += ['', name + ': ' + entry['purpose'], 'Input: ' + entry['input'], 'Outputs: ' + entry['outputs']]
    if mode in (None, 'scan'):
        lines += ['', 'Scan options: --depth quick|deep, --severity LEVEL, --format markdown|json|both,',
                  '--output PATH, --exclude RELATIVE_GLOB (repeatable), --offline, --no-tools.',
                  'Defaults: quick, informational, both, offline. Filters affect views, not canonical JSON.']
    lines += ['', 'Helper: recon.py request MODE TARGET validates the request only.',
              'Helper: recon.py scan-report TARGET imports local reports; no scanners are launched.',
              'Installer: panda-suite install/update copies skills; npx skills is not mode execution.',
              'Active testing, remote scans, installation and uploads require their own authorization.']
    if mode in (None, 'intel'):
        lines += ['', 'Intel: latest, update, status, owasp, cve CVE-ID, kev, incidents [--days N: default 1 for latest/update, 7 for incidents].',
                  'Helper intel requires --allow-network for live reads; --offline reads dated cache.',
                  'scan/hunt/incident accept --intel off|cache|live; explicit --offline conflicts with live.',
                  'Package queries need separate --allow-package-queries; no scheduler is activated.']
    return '\n'.join(lines)


def parse_request(argv, contract):
    parser = argparse.ArgumentParser(prog='panda-recon request', description='Validate an agent request without executing it.')
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
        if item['name'] == 'scan':
            options(command)
        elif item['name'] in ('hunt', 'incident'):
            command.add_argument('--intel', choices=['off', 'cache', 'live'], default='off')
            command.add_argument('--offline', action='store_true')
    args = parser.parse_args(argv)
    if args.mode == 'intel':
        import re
        days = args.days if args.days is not None else (7 if args.topic == 'incidents' else 1)
        if (not 1 <= days <= 120 or args.topic == 'cve' and not re.fullmatch(r'CVE-\d{4}-\d{4,19}', args.identifier or '')
                or args.topic != 'cve' and args.identifier is not None):
            raise ValueError('intel requires a valid topic/CVE and days 1–120')
        return {'schemaVersion': 'panda-recon.request/v1', 'mode': 'intel', 'topic': args.topic,
                'identifier': args.identifier, 'days': days, 'ecosystem': args.ecosystem,
                'severity': args.severity, 'offline': args.offline, 'executed': False,
                'permission': 'No execution; live public lookup intent does not authorize private package queries or probing'}
    path = args.target
    if path.is_symlink() or not path.exists() or not (path.is_file() or path.is_dir()):
        raise ValueError('invalid target: choose an existing authorized regular file or directory')
    if args.mode == 'scan' and not path.is_dir():
        raise ValueError('scan target must be a repository directory')
    result = {'schemaVersion': 'panda-recon.request/v1', 'mode': args.mode,
              'target': str(path.resolve()), 'executed': False, 'permission': 'local read-only request only'}
    if args.mode == 'scan':
        if args.offline and args.intel == 'live': raise ValueError('intel live conflicts with explicit offline')
        result['options'] = {'depth': args.depth, 'severity': args.severity, 'format': args.format,
                             'output': str(args.output) if args.output else None,
                             'exclude': args.exclude, 'offline': args.offline or args.intel != 'live', 'noTools': args.no_tools,
                             'intel': args.intel, 'networkScope': 'public-intelligence-only' if args.intel == 'live' else 'none'}
    elif args.mode in ('hunt', 'incident'):
        if args.offline and args.intel == 'live': raise ValueError('intel live conflicts with explicit offline')
        result['options'] = {'intel': args.intel, 'offline': args.offline or args.intel != 'live',
                             'networkScope': 'public-intelligence-only' if args.intel == 'live' else 'none'}
    return result
