"""Loopback-only HTTP API with optional real inference backend."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from . import __display_name__, __version__
from .backend import BackendError, LocalBackend

MAX_REQUEST_BYTES = 1024 * 1024


def health_document(backend: LocalBackend | None = None) -> dict:
    available = False
    if backend is not None:
        try:
            available = bool(backend.models().get("data"))
        except BackendError:
            pass
    return {
        "project": __display_name__,
        "version": __version__,
        "service": "running",
        "backend_configured": backend is not None,
        "inference_ready": available,
        "status": "ready" if available else "backend_unavailable",
    }


def models_document(backend: LocalBackend | None = None) -> dict:
    return backend.models() if backend is not None else {"object": "list", "data": []}


class SofiaHandler(BaseHTTPRequestHandler):
    server_version = "LogicaSofia/0.2"

    def _json(self, code: int, payload: dict) -> None:
        output = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(output)))
        self.end_headers()
        self.wfile.write(output)

    def _unavailable(self) -> None:
        self._json(503, {"error": {
            "message": "No reachable local inference backend is configured.",
            "type": "backend_unavailable",
        }})

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        backend = getattr(self.server, "backend", None)
        if path == "/health":
            self._json(200, health_document(backend))
        elif path == "/v1/models":
            try:
                self._json(200, models_document(backend))
            except BackendError:
                self._unavailable()
        else:
            self._json(404, {"error": {"message": "Not found", "type": "not_found"}})

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        if path != "/v1/chat/completions":
            self._json(404, {"error": {"message": "Not found", "type": "not_found"}})
            return
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._json(411, {"error": {"message": "Content-Length required"}})
            return
        if not (0 < length <= MAX_REQUEST_BYTES):
            self._json(413, {"error": {"message": "Request body empty or too large"}})
            return
        try:
            request = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json(400, {"error": {"message": "Malformed JSON"}})
            return
        if not isinstance(request, dict) or not isinstance(request.get("messages"), list):
            self._json(400, {"error": {"message": "A messages array is required"}})
            return
        if request.get("stream"):
            self._json(400, {"error": {"message": "Streaming is not implemented yet"}})
            return
        backend = getattr(self.server, "backend", None)
        if backend is None:
            self._unavailable()
            return
        try:
            status, response = backend.request("POST", "/v1/chat/completions", request)
            self._json(status, response)
        except BackendError:
            self._unavailable()


def serve(port: int = 8765, backend: LocalBackend | None = None) -> None:
    if not 1 <= port <= 65535:
        raise ValueError("port must be between 1 and 65535")
    # Keep unauthenticated API private to localhost, even if a model is available.
    with ThreadingHTTPServer(("127.0.0.1", port), SofiaHandler) as server:
        server.backend = backend
        print(f"LogicaSofia: http://127.0.0.1:{port}; backend={'configured' if backend else 'none'}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
