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
    parser.add_argument('--offline', action='store_true', default=True, help='default; no remote operations are permitted by this request')
    parser.add_argument('--no-tools', action='store_true', help='request manual/static work without launching external scanners')


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
    return '\n'.join(lines)


def parse_request(argv, contract):
    parser = argparse.ArgumentParser(prog='panda-recon request', description='Validate an agent request without executing it.')
    modes = parser.add_subparsers(dest='mode', required=True)
    for item in contract['modes']:
        command = modes.add_parser(item['name'], help=item['purpose'])
        command.add_argument('target', type=Path, help=item['input'])
        if item['name'] == 'scan':
            options(command)
    args = parser.parse_args(argv)
    path = args.target
    if path.is_symlink() or not path.exists() or not (path.is_file() or path.is_dir()):
        raise ValueError('invalid target: choose an existing authorized regular file or directory')
    if args.mode == 'scan' and not path.is_dir():
        raise ValueError('scan target must be a repository directory')
    result = {'schemaVersion': 'panda-recon.request/v1', 'mode': args.mode,
              'target': str(path.resolve()), 'executed': False, 'permission': 'local read-only request only'}
    if args.mode == 'scan':
        result['options'] = {'depth': args.depth, 'severity': args.severity, 'format': args.format,
                             'output': str(args.output) if args.output else None,
                             'exclude': args.exclude, 'offline': args.offline, 'noTools': args.no_tools}
    return result
