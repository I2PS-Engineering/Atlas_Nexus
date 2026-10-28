"""Optional, loopback-only model-backend adapter.

A compatible inference server (such as llama.cpp's HTTP server) is installed
and run separately. No model or runtime is downloaded automatically.
"""

from __future__ import annotations

import http.client
import json
from dataclasses import dataclass
from urllib.parse import urlsplit

MAX_RESPONSE_BYTES = 8 * 1024 * 1024


class BackendError(Exception):
    """Local model server is absent or returned an invalid response."""


@dataclass(frozen=True)
class LocalBackend:
    host: str
    port: int

    @classmethod
    def from_url(cls, url: str) -> "LocalBackend":
        """Reject remote hosts, URL credentials, paths and non-HTTP protocols."""
        try:
            parsed = urlsplit(url)
            port = parsed.port
        except ValueError as exc:
            raise ValueError("Invalid backend URL") from exc
        if (parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "::1")
                or parsed.username or parsed.password or parsed.path not in ("", "/")
                or parsed.query or parsed.fragment or port is None
                or not (1 <= port <= 65535)):
            raise ValueError("Backend must be http://127.0.0.1:PORT or http://[::1]:PORT")
        return cls(host=parsed.hostname, port=port)

    def request(self, method: str, path: str, payload: dict | None = None,
                timeout: float = 15.0) -> tuple[int, dict]:
        """Forward one fixed API request; do not follow redirects."""
        if (method, path) not in {
            ("GET", "/v1/models"),
            ("POST", "/v1/chat/completions"),
        }:
            raise ValueError("Unsupported backend operation")
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
        connection = http.client.HTTPConnection(self.host, self.port, timeout=timeout)
        try:
            connection.request(method, path, body=body,
                               headers={"Content-Type": "application/json"} if body is not None else {})
            response = connection.getresponse()
            # Explicit response cap protects the gateway from oversized output.
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise BackendError("Backend response exceeds size limit")
            try:
                result = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise BackendError("Backend did not return valid JSON") from exc
            if not isinstance(result, dict):
                raise BackendError("Backend JSON response must be an object")
            if not (200 <= response.status < 300 or 400 <= response.status < 500):
                raise BackendError(f"Backend returned HTTP {response.status}")
            return response.status, result
        except (OSError, TimeoutError, http.client.HTTPException) as exc:
            raise BackendError("Local inference backend unavailable") from exc
        finally:
            connection.close()

    def models(self, timeout: float = 2.0) -> dict:
        code, data = self.request("GET", "/v1/models", timeout=timeout)
        if code != 200 or not isinstance(data.get("data"), list):
            raise BackendError("Backend model listing is unavailable")
        return data
