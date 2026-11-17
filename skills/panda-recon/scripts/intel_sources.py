"""Bounded official source adapters. Returned text is untrusted evidence, never commands."""

from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
import json
import re
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

CVE = re.compile(r'CVE-[0-9]{4}-[0-9]{4,19}\Z')
NVD_PAGE = 1000          # About 3.6 MB per live page, inside the 8 MiB response cap.
NVD_MAX_RECORDS = 8000   # Per run; a larger window is refused rather than truncated.
NVD_CACHE_RECORDS = 12000


def compact_nvd(row):
    """Window snapshots keep only the fields normalization uses; single-CVE lookups stay complete."""
    metrics = {}
    for group, values in row.get('metrics', {}).items():
        metrics[group] = [{'cvssData': {k: m.get('cvssData', {}).get(k) for k in ('version', 'baseScore', 'baseSeverity', 'vectorString')},
                           'baseSeverity': m.get('baseSeverity')} for m in values]
    english = [d for d in row['descriptions'] if d.get('lang') == 'en'][:1]
    return {'id': row['id'], 'vulnStatus': row.get('vulnStatus'), 'published': row['published'],
            'lastModified': row['lastModified'], 'metrics': metrics,
            'descriptions': [{'lang': 'en', 'value': d['value'][:1000]} for d in english],
            'references': [{'url': r.get('url'), 'source': r.get('source')} for r in row.get('references', [])[:5]]}


def cve_id(value):
    if not isinstance(value, str) or not CVE.fullmatch(value): raise ValueError('invalid CVE identifier')
    return value


def iso(value, nvd=False):
    if value is None: return None
    if not isinstance(value, str): raise ValueError('invalid timestamp')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        if not nvd: raise ValueError('missing timestamp offset')
        parsed = parsed.replace(tzinfo=timezone.utc)  # NVD API timestamps are UTC.
    return parsed.isoformat()


def decode(raw):
    def pairs(items):
        data = {}
        for key, value in items:
            if key in data: raise ValueError('duplicate response field')
            data[key] = value
        return data
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('invalid numeric value')))


class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.words = []; self.hidden = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.hidden += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.hidden = max(0, self.hidden - 1)
    def handle_data(self, data):
        if not self.hidden: self.words.append(data)


def fetch(source, query, client, config, now, previous=None):
    endpoint = config[source]['endpoint']
    urls = []
    def get(params=None, payload=None):
        url = endpoint + ('?' + urlencode(params) if params else '')
        urls.append(url)
        raw = client.fetch(source, url, payload)
        return raw
    if source == 'nvd':
        records, offset = [], 0
        params = {'resultsPerPage': NVD_PAGE}
        if query.get('cve'):
            params['cveId'] = cve_id(query['cve'])
        else:
            end = datetime.fromisoformat(now)
            start = end - timedelta(days=query.get('days', 7))
            if previous:
                old = datetime.fromisoformat(previous['retrievedAt'].replace('Z', '+00:00')) - timedelta(minutes=2)
                if query.get('sync') and not query.get('restart'):
                    if end - old > timedelta(days=120): raise ValueError('NVD catch-up window exceeds 120 days; explicit partitioning required')
                    start = old
                elif query.get('sync'): pass  # Explicit restart: the caller accepted the gap and reports it.
                else: start = max(start, old)
            params.update(lastModStartDate=start.isoformat(), lastModEndDate=end.isoformat())
        for _ in range(NVD_MAX_RECORDS // NVD_PAGE + 1):
            page = decode(get(dict(params, startIndex=offset)))
            if (not isinstance(page, dict) or type(page.get('totalResults')) is not int or page['totalResults'] < 0
                    or not isinstance(page.get('vulnerabilities'), list) or page.get('startIndex') != offset):
                raise ValueError('NVD response schema changed')
            if page['totalResults'] > NVD_MAX_RECORDS: raise ValueError('NVD_WINDOW_TOO_LARGE')
            rows = page['vulnerabilities']
            for wrapper in rows:
                row = wrapper['cve']; cve_id(row['id']); iso(row['published'], True); iso(row['lastModified'], True)
                if query.get('cve') and row['id'] != query['cve']: raise ValueError('CVE subject mismatch')
                if not isinstance(row.get('descriptions'), list): raise ValueError('NVD descriptions missing')
                records.append(row if query.get('cve') else compact_nvd(row))
            offset += len(rows)
            if offset >= page['totalResults']: break
            if not rows: raise ValueError('NVD incomplete pagination')
        else: raise ValueError('NVD pagination cap; prior snapshot retained')
        if len({r['id'] for r in records}) != len(records): raise ValueError('duplicate NVD subjects')
        if previous and not query.get('cve'):
            merged = {r['id']: r for r in previous['data']['records']}
            merged.update({r['id']: r for r in records})
            # Keep only changes inside the query window; older ones were reported by earlier runs.
            keep_after = datetime.fromisoformat(now) - timedelta(days=query.get('days', 1))
            records = [r for r in merged.values() if iso(r['lastModified'], True) and
                       datetime.fromisoformat(iso(r['lastModified'], True)) >= keep_after]
        if len(records) > NVD_CACHE_RECORDS: raise ValueError('NVD cache record cap')
        return {'records': records, 'urls': urls, 'sourceVersion': str(page.get('version')) if page.get('version') else None}
    if source == 'kev':
        data = decode(get())
        rows = data['vulnerabilities']
        if not isinstance(rows, list) or data.get('count', len(rows)) != len(rows): raise ValueError('KEV count/schema mismatch')
        iso(data['dateReleased'])
        for row in rows:
            cve_id(row['cveID']); datetime.fromisoformat(row['dateAdded']); row['requiredAction']
        return {'records': rows, 'urls': urls, 'sourceVersion': data.get('catalogVersion'), 'catalogDate': data['dateReleased']}
    if source == 'epss':
        ids = query.get('cves', [])
        if not ids or len(ids) > 50: raise ValueError('EPSS requires 1–50 explicit CVEs')
        for value in ids: cve_id(value)
        data = decode(get({'cve': ','.join(ids), 'limit': 100}))
        if data.get('status') != 'OK' or not isinstance(data.get('data'), list): raise ValueError('EPSS schema/status changed')
        rows = data['data']
        for row in rows:
            if cve_id(row['cve']) not in ids: raise ValueError('EPSS subject mismatch')
            if not 0 <= float(row['epss']) <= 1 or not 0 <= float(row['percentile']) <= 1:
                raise ValueError('invalid EPSS probability')
            datetime.fromisoformat(row['date'])
        if data.get('total', len(rows)) != len(rows): raise ValueError('EPSS incomplete response')
        return {'records': rows, 'urls': urls, 'sourceVersion': data.get('version'), 'modelVersion': data.get('modelVersion')}
    if source == 'osv':
        package = query['package']; version = query['version']
        if not isinstance(version, str) or not version: raise ValueError('OSV needs exact supplied version')
        payload = {'package': package, 'version': version}; records = []
        for _ in range(3):
            data = decode(get(payload=payload))
            if not isinstance(data, dict) or not isinstance(data.get('vulns', []), list): raise ValueError('OSV schema changed')
            for row in data.get('vulns', []):
                if not isinstance(row.get('id'), str) or not isinstance(row.get('affected'), list): raise ValueError('OSV advisory schema changed')
                for affected in row['affected']:
                    if (not isinstance(affected, dict) or not isinstance(affected.get('package'), dict)
                            or not isinstance(affected['package'].get('name'), str)
                            or not isinstance(affected['package'].get('ecosystem'), str)
                            or not isinstance(affected.get('ranges', []), list)
                            or not isinstance(affected.get('versions', []), list)):
                        raise ValueError('OSV affected package schema changed')
                iso(row.get('published')); iso(row.get('modified')); iso(row.get('withdrawn'))
                records.append(row)
            token = data.get('next_page_token')
            if not token: break
            if not isinstance(token, str) or len(token) > 4096: raise ValueError('invalid OSV cursor')
            payload = dict(payload, page_token=token)
        else: raise ValueError('OSV pagination cap; prior snapshot retained')
        if len(records) > 5000: raise ValueError('OSV record cap')
        return {'records': records, 'urls': urls, 'sourceVersion': None, 'queryPackage': package, 'queryVersion': version}
    if source.startswith('owasp-'):
        parser = Text(); parser.feed(get().decode('utf-8'))
        text = re.sub(r'\s+', ' ', ' '.join(parser.words))
        patterns = {'owasp-web': r'most current released version is (?:the )?OWASP Top 10[: ]+(\d{4})',
                    'owasp-api': r'(?:latest|current) (?:published |released )?(?:version|edition)[^\d]{0,60}(20\d{2})',
                    'owasp-asvs': r'Download ASVS\s+(\d+\.\d+\.\d+)'}
        match = re.search(patterns[source], text, re.I)
        version = match[1] if match else None
        # No max-year heuristic: missing/changed release language remains unknown.
        return {'records': [{'id': source, 'title': config[source]['name'], 'sourceVersion': version,
                             'publishedAt': None, 'modifiedAt': None, 'releaseClaim': match[0] if match else None,
                             'interpretationRequired': True}], 'urls': urls, 'sourceVersion': version}
    if source == 'mitre':
        data = decode(get()); collections = data['collections']
        if not isinstance(collections, list): raise ValueError('MITRE index schema changed')
        rows = []
        for collection in collections:
            versions = collection['versions']
            if not isinstance(versions, list): raise ValueError('MITRE versions missing')
            rows.append({'id': collection['id'], 'title': collection['name'], 'versions': versions,
                         'techniqueCatalogLoaded': False})
        return {'records': rows, 'urls': urls, 'sourceVersion': None}
    if source == 'incidents':
        raw = get()
        if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper(): raise ValueError('DTD/entity content refused')
        tree = ET.fromstring(raw)
        rows = []
        for item in tree.findall('.//item')[:200]:
            title, link, published = item.findtext('title'), item.findtext('link'), item.findtext('pubDate')
            if not title or not link or not link.startswith('https://'): raise ValueError('advisory feed schema changed')
            when = parsedate_to_datetime(published).isoformat() if published else None
            rows.append({'id': link, 'title': title[:2000], 'publishedAt': when, 'modifiedAt': None,
                         'occurredAt': None, 'firstDisclosureAt': None, 'confirmedFacts': [],
                         'unverifiedClaims': [title[:2000]], 'classification': 'Advisory lead, not a confirmed incident'})
        if not tree.findall('.//channel'): raise ValueError('unsupported advisory feed')
        return {'records': rows, 'urls': urls, 'sourceVersion': None}
    raise ValueError('unsupported source')
