"""Bounded HTTPS transport, raw responses, cache and redactable audit trail."""
from __future__ import annotations
import hashlib
import ipaddress
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

def now():
    return datetime.now(timezone.utc).isoformat()

def atomic_json(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, p)

def redacted_url(url):
    p = urlsplit(url)
    pairs = [(k, "REDACTED" if any(s in k.lower() for s in ("key", "token", "secret", "signature", "password")) else v) for k, v in parse_qsl(p.query, keep_blank_values=True)]
    return urlunsplit((p.scheme, p.netloc, p.path, urlencode(pairs), ""))

def allowed_url(url):
    try:
        p = urlsplit(url)
        if p.scheme not in ("http", "https") or not p.hostname or p.username or p.password:
            return False
        if p.hostname.lower() in ("localhost", "localhost.localdomain") or p.hostname.lower().endswith(".local"):
            return False
        try:
            return ipaddress.ip_address(p.hostname).is_global
        except ValueError:
            return True
    except ValueError:
        return False

@dataclass
class Response:
    status: int
    body: bytes
    content_type: str = ""
    headers: dict | None = None
    url: str = ""
    raw_path: str = ""
    error: str = ""
    cached: bool = False
    def text(self):
        return self.body.decode("utf-8-sig", errors="replace")
    def json(self):
        return json.loads(self.text())

def blocked(body):
    text = body[:100000].decode("utf-8", errors="ignore").lower()
    return any(s in text for s in ("verify you are human", "verificando seu navegador", "validamos sua conexão", "cf-chl-", "just a moment...", "checking your browser", "captcha-container", "access denied"))

class Client:
    def __init__(self, root, timeout=20, retries=2, opener=None, sleeper=None):
        self.root = Path(root)
        self.timeout, self.retries = timeout, retries
        self.opener = opener or urlopen
        self.sleep = sleeper or time.sleep
        self.events = []

    def invalidate(self, response):
        if response.raw_path:
            Path(response.raw_path).with_suffix(".json").unlink(missing_ok=True)

    def get(self, base, params=None, headers=None, cache=True, max_bytes=12_000_000):
        url = base + (("&" if "?" in base else "?") + urlencode(params, doseq=True) if params else "")
        if not allowed_url(url):
            return Response(0, b"", url=redacted_url(url), error="unsupported_or_nonpublic_url")
        safe = redacted_url(url)
        # Tokens also identify pagination. Redact logs, but never collapse distinct
        # requests into the same cache key. Header values remain only in this hash.
        signature = json.dumps({"url": url, "headers": headers or {}}, sort_keys=True)
        ident = hashlib.sha256(signature.encode()).hexdigest()
        raw = self.root / "raw" / (ident + ".bin")
        meta = raw.with_suffix(".json")
        if cache and raw.exists() and meta.exists():
            m = json.loads(meta.read_text(encoding="utf-8"))
            response = Response(m["status"], raw.read_bytes(), m["content_type"], url=safe, raw_path=str(raw), cached=True)
            self.events.append({"url": safe, "at": now(), "status": response.status, "cached": True, "raw_path": str(raw)})
            return response
        response = Response(0, b"", url=safe, error="not_attempted")
        for attempt in range(self.retries + 1):
            try:
                request = Request(url, headers={"User-Agent": "BuscaAcademica/1.0 (academic metadata research)", "Accept": "application/json, application/xml, text/html;q=0.8", **(headers or {})})
                with self.opener(request, timeout=self.timeout) as handle:
                    final_url = handle.geturl() if hasattr(handle, "geturl") else url
                    if not allowed_url(final_url):
                        response = Response(0, b"", url=safe, error="nonpublic_redirect")
                        break
                    body = handle.read(max_bytes + 1)
                    if len(body) > max_bytes:
                        response = Response(0, b"", url=safe, error="response_too_large")
                        break
                    response = Response(handle.status, body, handle.headers.get("Content-Type", ""), dict(handle.headers), safe)
            except HTTPError as exc:
                response = Response(exc.code, exc.read(100000), exc.headers.get("Content-Type", ""), dict(exc.headers), safe, error="http_error")
            except (URLError, TimeoutError, OSError) as exc:
                response = Response(0, b"", url=safe, error=type(exc).__name__)
            self.events.append({"url": safe, "at": now(), "status": response.status, "attempt": attempt + 1, "error": response.error})
            if response.status not in (429, 500, 502, 503, 504, 0) or attempt == self.retries:
                break
            value = (response.headers or {}).get("Retry-After", "")
            try:
                delay = float(value)
            except (ValueError, TypeError):
                try:
                    delay = (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()
                except (ValueError, TypeError, OverflowError):
                    delay = 2 ** attempt
            self.sleep(min(max(delay, 0), 30))
        raw.parent.mkdir(parents=True, exist_ok=True)
        # Keep failed responses for diagnosis; reuse only successful non-challenge responses.
        raw.write_bytes(response.body)
        response.raw_path = str(raw)
        atomic_json(raw.with_suffix(".response.json"), {"url": safe, "status": response.status, "content_type": response.content_type, "error": response.error, "at": now()})
        if 200 <= response.status < 300 and not blocked(response.body) and cache:
            atomic_json(meta, {"status": response.status, "content_type": response.content_type, "at": now()})
        return response
