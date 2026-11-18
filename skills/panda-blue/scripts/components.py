"""Local inventory and conservative exact package/version applicability. No installs."""

import re

ECOSYSTEMS = {'go': 'Go', 'Go': 'Go', 'npm': 'npm', 'pypi': 'PyPI', 'PyPI': 'PyPI', 'Maven': 'Maven', 'crates.io': 'crates.io', 'NuGet': 'NuGet'}


def validate(rows):
    if not isinstance(rows, list) or len(rows) > 1000: raise ValueError('invalid component inventory')
    result = []
    for row in rows:
        if not isinstance(row, dict) or not {'name', 'ecosystem', 'version'} <= set(row): raise ValueError('component fields missing')
        if (not isinstance(row['name'], str) or not 1 <= len(row['name']) <= 256
                or not re.fullmatch(r'[A-Za-z0-9@._/+:~-]+', row['name']) or row['ecosystem'] not in ECOSYSTEMS):
            raise ValueError('unsupported component identity')
        version = row['version']
        if version is not None and (not isinstance(version, str) or not re.fullmatch(r'[A-Za-z0-9._+~:-]{1,128}', version)):
            raise ValueError('invalid component version')
        item = dict(row, ecosystem=ECOSYSTEMS[row['ecosystem']])
        if item.get('versionKind', 'provided') not in {'provided', 'resolved', 'declared'}: raise ValueError('invalid version evidence')
        if 'backport' in item and type(item['backport']) is not bool: raise ValueError('invalid backport claim')
        if 'internetExposed' in item and type(item['internetExposed']) is not bool: raise ValueError('invalid exposure claim')
        result.append(item)
    return result


def inventory(root, load_json):
    path = root / 'package-lock.json'
    rows = []
    if path.exists():
        data = load_json(path)
        if data.get('lockfileVersion') not in (2, 3) or not isinstance(data.get('packages'), dict):
            raise ValueError('only npm package-lock v2/v3 is supported automatically')
        for key, item in data['packages'].items():
            if 'node_modules/' in key:
                rows.append({'name': key.rsplit('node_modules/', 1)[1], 'ecosystem': 'npm',
                             'version': None if item.get('link') else item.get('version'),
                             'versionKind': 'resolved', 'evidence': 'package-lock.json:' + key})
    # Other ecosystems need an explicit reviewed inventory; go.sum is not an installed graph.
    unique = {(r['ecosystem'], r['name'], r['version']): r for r in rows}
    return validate(list(unique.values()))


def semver(value):
    match = re.fullmatch(r'v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?', value)
    if not match: raise ValueError('unsupported version syntax')
    prerelease = match[4]
    identifiers = []
    if prerelease:
        for part in prerelease.split('.'):
            if not part or part.isdigit() and len(part) > 1 and part.startswith('0'): raise ValueError('invalid prerelease')
            identifiers.append((0, int(part)) if part.isdigit() else (1, part))
    return tuple(int(match[i]) for i in (1, 2, 3)), (0, tuple(identifiers)) if prerelease else (1, ())


def affected(component, advisory):
    if advisory.get('withdrawn'): return 'Not affected', 'Advisory is withdrawn; not a remediation claim.'
    if not component.get('version'): return 'Version unknown', 'No resolved/provided version evidence.'
    packages = [row for row in advisory.get('affected', [])
                if row.get('package', {}).get('ecosystem') == component['ecosystem']
                and row.get('package', {}).get('name') == component['name']]
    if not packages: return 'Insufficient evidence', 'No exact ecosystem/name identity match; no fuzzy correlation.'
    if component.get('backport'): return 'Insufficient evidence', 'Backport/vendor branch needs authoritative vendor evidence.'
    answer = False; uncertain = False
    for package in packages:
        if component['version'] in package.get('versions', []): answer = True; continue
        ranges = package.get('ranges', [])
        if not ranges and not package.get('versions'): uncertain = True
        for interval in ranges:
            if interval.get('type') != 'SEMVER' or component['ecosystem'] not in {'npm', 'Go'}:
                uncertain = True; continue
            try:
                version = semver(component['version']); start = None; open_range = False
                for event in interval['events']:
                    if 'introduced' in event:
                        start = None if event['introduced'] == '0' else semver(event['introduced']); open_range = True
                    else:
                        kind = next(k for k in ('fixed', 'last_affected', 'limit') if k in event)
                        end = semver(event[kind])
                        if not open_range: raise ValueError('range lacks introduction')
                        answer |= (start is None or version >= start) and (version <= end if kind == 'last_affected' else version < end)
                        open_range = False
                if open_range: answer |= start is None or version >= start
            except (ValueError, KeyError, StopIteration, TypeError): uncertain = True
    if answer:
        if component.get('versionKind') == 'declared':
            return 'Potentially affected component', 'Declared constraint is not a resolved/deployed version.'
        return 'Confirmed affected component', 'Exact package identity and explicit version/SEMVER membership; deployment and reachability unverified.'
    if uncertain: return 'Potentially affected component', 'Unsupported range/version semantics require ecosystem/vendor verification.'
    return 'Not affected', 'Version outside supported explicit/SEMVER ranges in this advisory only.'
