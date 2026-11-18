"""Verified-TLS, fixed-endpoint HTTP. No redirects, downloads/execution or arbitrary URLs."""

import json
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import math
from pathlib import Path
import ssl
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPSHandler, HTTPRedirectHandler, ProxyHandler, Request, build_opener

MAX_BYTES = 8 * 1024 * 1024
MAX_REQUESTS = 40      # Per run: up to 9 NVD pages plus KEV, EPSS, OSV and guidance sources.
MAX_SECONDS = 240      # Per run, including NVD's recommended 6-second spacing.
REQUEST_TIMEOUT = 30   # One 1,000-record NVD page is about 3.6 MB.


class SourceError(ValueError):
    def __init__(self, code, retry_after=None):
        super().__init__(code)
        self.code, self.retry_after = code, retry_after


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise SourceError('REDIRECT_BLOCKED')


def https_url(url):
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username is not None
            or parsed.password is not None or parsed.fragment or parsed.port not in (None, 443)):
        raise SourceError('UNSAFE_SOURCE_URL')
    return parsed


def http(url, method, payload, timeout):
    https_url(url)
    # System trust remains verified; no unverified SSL context or fallback transport.
    cafile = '/etc/ssl/cert.pem' if Path('/etc/ssl/cert.pem').is_file() else None
    context = ssl.create_default_context(cafile=cafile)
    opener = build_opener(ProxyHandler({}), HTTPSHandler(context=context), NoRedirect())
    body = json.dumps(payload, allow_nan=False).encode() if payload is not None else None
    request = Request(url, data=body, method=method,
                      headers={'Accept': 'application/json, text/html, application/rss+xml, application/xml',
                               'Content-Type': 'application/json', 'User-Agent': 'Panda-Blue-Intel/0.4 (+https://github.com/refactorroom/panda-suite)'})
    started = time.monotonic()
    try:
        with opener.open(request, timeout=timeout) as response:
            if response.geturl() != url:
                raise SourceError('REDIRECT_BLOCKED')
            kind = response.headers.get('Content-Type', '').lower()
            content = bytearray()
            while True:
                if time.monotonic() - started > timeout:
                    raise SourceError('TIMEOUT')
                block = response.read(min(65536, MAX_BYTES + 1 - len(content)))
                if not block:
                    break
                content.extend(block)
                if len(content) > MAX_BYTES:
                    raise SourceError('RESPONSE_TOO_LARGE')
            return bytes(content), kind
    except HTTPError as error:
        if 300 <= error.code < 400:
            raise SourceError('REDIRECT_BLOCKED') from error
        retry = error.headers.get('Retry-After', '')
        delay = float(retry) if retry.isdigit() else None
        if retry and delay is None:
            try:
                delay = max(0, (parsedate_to_datetime(retry) - datetime.now(timezone.utc)).total_seconds())
            except (ValueError, TypeError): pass
        raise SourceError('HTTP_' + str(error.code), delay) from error
    except (URLError, TimeoutError, OSError) as error:
        raise SourceError('NETWORK_OR_TLS_UNAVAILABLE') from error


class Client:
    def __init__(self, endpoints, allow_network=False, transport=http, sleep=time.sleep, clock=time.monotonic):
        self.endpoints, self.allow_network = endpoints, allow_network
        self.transport, self.sleep, self.clock = transport, sleep, clock
        self.started, self.last_nvd = clock(), None
        self.requests = []

    def fetch(self, source, url, payload=None):
        endpoint = self.endpoints[source]['endpoint']
        if url.split('?', 1)[0] != endpoint:
            raise SourceError('DESTINATION_NOT_ALLOWLISTED')
        https_url(url)
        if not self.allow_network:
            raise SourceError('NETWORK_NOT_AUTHORIZED')
        if len(self.requests) >= MAX_REQUESTS or self.clock() - self.started >= MAX_SECONDS:
            raise SourceError('REQUEST_BUDGET_EXHAUSTED')
        for attempt in range(3):
            elapsed = self.clock() - self.started
            if elapsed >= MAX_SECONDS or len(self.requests) >= MAX_REQUESTS:
                raise SourceError('REQUEST_BUDGET_EXHAUSTED')
            if source == 'nvd' and self.last_nvd is not None:
                self.sleep(max(0, 6 - (self.clock() - self.last_nvd)))
            self.requests.append({'source': source, 'url': url, 'method': 'POST' if payload is not None else 'GET',
                                  'bodySent': payload is not None, 'attempt': attempt + 1})
            if source == 'nvd': self.last_nvd = self.clock()
            try:
                data, kind = self.transport(url, 'POST' if payload is not None else 'GET', payload, min(REQUEST_TIMEOUT, max(1, MAX_SECONDS - elapsed)))
                if not isinstance(data, bytes) or len(data) > MAX_BYTES:
                    raise SourceError('INVALID_OR_OVERSIZED_RESPONSE')
                expected = self.endpoints[source]['format']
                official_raw_json = (source in ('kev', 'mitre') and endpoint.startswith('https://raw.githubusercontent.com/')
                                     and 'text/plain' in kind)
                if (expected == 'json' and 'json' not in kind and not official_raw_json or expected == 'html' and 'html' not in kind
                        or expected == 'xml' and not any(v in kind for v in ('xml', 'rss'))):
                    raise SourceError('CONTENT_TYPE_CHANGED')
                return data
            except SourceError as error:
                transient = error.code in {'HTTP_429', 'HTTP_500', 'HTTP_502', 'HTTP_503', 'HTTP_504', 'NETWORK_OR_TLS_UNAVAILABLE'}
                delay = error.retry_after if error.retry_after is not None else 2 ** (attempt + 1)
                if not transient or attempt == 2 or not math.isfinite(delay) or delay > 30:
                    raise
                self.sleep(max(0, delay))
        raise SourceError('SOURCE_UNAVAILABLE')
