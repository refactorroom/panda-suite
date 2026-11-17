"""Private append-only snapshots and atomic status pointers; no refresh on cache reads."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import uuid
import time

LIMIT = 16 * 1024 * 1024


def stamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timestamp must have an offset')
    return result


def read(path, with_bytes=False):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > LIMIT:
        raise ValueError('invalid cache file')
    with path.open('rb') as stream:
        raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT: raise ValueError('cache size exceeded')
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result: raise ValueError('duplicate cache key')
            result[k] = v
        return result
    value = json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('non-finite cache value')))
    return (value, raw) if with_bytes else value


def key(source, query):
    return hashlib.sha256(json.dumps([source, query], sort_keys=True).encode()).hexdigest()


class Store:
    def __init__(self, root):
        self.root = Path(root).absolute()
        for path in [self.root, *self.root.parents]:
            if path.is_symlink(): raise ValueError('linked cache anchor refused; use a canonical path')

    def state(self):
        path = self.root / 'state.json'
        if not path.exists(): return {'schemaVersion': 'panda-recon.intel-cache/v1', 'entries': {}}
        data = read(path)
        if data.get('schemaVersion') != 'panda-recon.intel-cache/v1' or not isinstance(data.get('entries'), dict):
            raise ValueError('invalid cache state')
        return data

    def snapshot(self, source, query):
        entry = self.state()['entries'].get(key(source, query))
        if not entry or not entry.get('snapshot'): return None, entry
        name = entry['snapshot']
        if Path(name).name != name or not name.endswith('.json'): raise ValueError('unsafe snapshot reference')
        path = self.root / name
        data, raw = read(path, with_bytes=True)
        if hashlib.sha256(raw).hexdigest() != entry.get('sha256'):
            raise ValueError('snapshot integrity mismatch')
        if data.get('source') != source or data.get('query') != query:
            raise ValueError('snapshot subject mismatch')
        stamp(data['retrievedAt'])
        return data, entry

    def commit(self, source, query, now, data=None, error=None):
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if os.name != 'nt' and self.root.stat().st_mode & 0o077:
            raise ValueError('cache directory must be private (0700)')
        lock = self.root / '.write-lock'
        for attempt in range(3):
            try:
                lock.mkdir(mode=0o700)
                break
            except FileExistsError:
                if attempt == 2: raise ValueError('CACHE_BUSY; inspect interrupted/concurrent writer')
                time.sleep(0.05 * (attempt + 1))
        try:
            return self._commit(source, query, now, data, error)
        finally:
            lock.rmdir()

    def _commit(self, source, query, now, data, error):
        state = self.state(); k = key(source, query)
        entry = dict(state['entries'].get(k, {}))
        entry.update(source=source, query=query, lastAttempt=now, lastError=error)
        if data is not None:
            name = 'snapshot-' + uuid.uuid4().hex + '.json'
            payload = json.dumps({'source': source, 'query': query, 'retrievedAt': now, 'data': data},
                                 ensure_ascii=True, allow_nan=False, sort_keys=True).encode()
            if len(payload) > LIMIT: raise ValueError('snapshot too large')
            self._write(self.root / name, payload)
            entry.update(snapshot=name, sha256=hashlib.sha256(payload).hexdigest(), lastSuccess=now)
        state['entries'][k] = entry
        temp = self.root / ('.state-' + uuid.uuid4().hex)
        self._write(temp, json.dumps(state, ensure_ascii=True, allow_nan=False).encode())
        os.replace(temp, self.root / 'state.json')
        return entry

    def _write(self, path, payload):
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(payload)


def freshness(snapshot, ttl, now):
    if snapshot is None: return {'status': 'Unavailable', 'ageSeconds': None}
    age = (stamp(now) - stamp(snapshot['retrievedAt'])).total_seconds()
    return {'status': 'Fresh' if 0 <= age < ttl else 'Stale', 'ageSeconds': max(0, int(age))}
