import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from logicasofia.backend import LocalBackend, BackendError


class Stub(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path != "/v1/models":
            self.send_error(404)
            return
        self.reply({"object": "list", "data": [{"id": "test-gguf"}]})

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.reply({"choices": [{"message": {"role": "assistant", "content": "backend response"}}], "model": data["model"]})

    def reply(self, data):
        raw = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


class BackendTests(unittest.TestCase):
    def test_accepts_loopback(self):
        self.assertEqual(LocalBackend.from_url("http://127.0.0.1:8080").port, 8080)
        self.assertEqual(LocalBackend.from_url("http://[::1]:8080").host, "::1")

    def test_rejects_remote_or_ambiguous_urls(self):
        for url in ["https://127.0.0.1:8080", "http://example.com:8080", "http://localhost:8080",
                    "http://127.0.0.1:8080/evil", "http://127.0.0.1", "http://x@127.0.0.1:8080",
                    "http://127.0.0.1:8080?x=1", "http://127.0.0.1:99999", "file:///etc/passwd"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                LocalBackend.from_url(url)

    def test_backend_pass_through(self):
        with ThreadingHTTPServer(("127.0.0.1", 0), Stub) as server:
            runner = threading.Thread(target=server.serve_forever, daemon=True)
            runner.start()
            backend = LocalBackend("127.0.0.1", server.server_address[1])
            self.assertEqual(backend.models()["data"][0]["id"], "test-gguf")
            status, data = backend.request("POST", "/v1/chat/completions", {"messages": [], "model": "test-gguf"})
            self.assertEqual(status, 200)
            self.assertEqual(data["choices"][0]["message"]["content"], "backend response")
            server.shutdown()
            runner.join()

    def test_unsupported_path_blocked(self):
        with self.assertRaises(ValueError):
            LocalBackend("127.0.0.1", 1).request("GET", "/internal/secrets")

    def test_unreachable_backend(self):
        with self.assertRaises(BackendError):
            LocalBackend("127.0.0.1", 1).models(timeout=0.25)


if __name__ == "__main__":
    unittest.main()
