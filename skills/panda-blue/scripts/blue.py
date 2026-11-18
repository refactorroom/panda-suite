#!/usr/bin/env python3
"""panda-blue offline case utilities and on-demand public intelligence. Never contacts assessment targets."""

import argparse
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=8)
def support(name):
    if name not in {'case_core', 'commands', 'intel', 'intel_sources', 'intel_store', 'intel_net', 'components'}:
        raise ValueError('unknown bundled helper module')
    spec = importlib.util.spec_from_file_location('_panda_blue_' + name, BASE / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_core = support('case_core')
MAX_JSON, MAX_ARTIFACT, MAX_TOTAL_ARTIFACT = _core.MAX_JSON, _core.MAX_ARTIFACT, _core.MAX_TOTAL_ARTIFACT
TRANSITIONS = _core.TRANSITIONS
pairs, invalid_constant, finite_float = _core.pairs, _core.invalid_constant, _core.finite_float
load_json, timestamp, validators, validate = _core.load_json, _core.timestamp, _core.validators, _core.validate
relative_path, check_integrity, transition, render = _core.relative_path, _core.check_integrity, _core.transition, _core.render


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
    command = commands.add_parser('validate')
    command.add_argument('kind', choices=['case', 'asset', 'finding', 'evidence', 'intelligence'])
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
