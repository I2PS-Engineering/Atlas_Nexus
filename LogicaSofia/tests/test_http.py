import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from logicasofia.service import SofiaHandler


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), SofiaHandler)
        cls.server.backend = None
        cls.runner = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.runner.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.runner.join()
        cls.server.server_close()

    def call(self, method, path, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_address[1], timeout=5)
        conn.request(method, path, body=body, headers={"Content-Type": "application/json"})
        response = conn.getresponse()
        result = response.status, json.loads(response.read())
        conn.close()
        return result

    def test_health(self):
        status, value = self.call("GET", "/health")
        self.assertEqual(status, 200)
        self.assertFalse(value["inference_ready"])

    def test_models_empty(self):
        status, value = self.call("GET", "/v1/models")
        self.assertEqual(status, 200)
        self.assertEqual(value["data"], [])

    def test_chat_requires_backend(self):
        status, value = self.call("POST", "/v1/chat/completions", b'{"model":"demo","messages":[]}')
        self.assertEqual(status, 503)
        self.assertEqual(value["error"]["type"], "backend_unavailable")

    def test_chat_rejects_malformed_json(self):
        self.assertEqual(self.call("POST", "/v1/chat/completions", b'{')[0], 400)

    def test_chat_rejects_streaming(self):
        self.assertEqual(self.call("POST", "/v1/chat/completions", b'{"messages":[],"stream":true}')[0], 400)

    def test_unknown_endpoint(self):
        self.assertEqual(self.call("GET", "/anything")[0], 404)


if __name__ == "__main__":
    unittest.main()
