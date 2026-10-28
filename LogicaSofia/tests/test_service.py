import unittest
from logicasofia.service import health_document, models_document


class ServiceTests(unittest.TestCase):
    def test_health_is_not_inference_ready_without_backend(self):
        doc = health_document()
        self.assertEqual(doc["project"], "LogicaSofia")
        self.assertFalse(doc["inference_ready"])
        self.assertFalse(doc["backend_configured"])
        self.assertEqual(doc["service"], "running")

    def test_no_ghost_models(self):
        self.assertEqual(models_document(), {"object": "list", "data": []})

    def test_backend_healthy_when_models_available(self):
        class FakeBackend:
            def models(self):
                return {"object": "list", "data": [{"id": "test-model"}]}
        self.assertTrue(health_document(FakeBackend())["inference_ready"])

    def test_empty_model_list_not_ready(self):
        class FakeBackend:
            def models(self):
                return {"data": []}
        self.assertFalse(health_document(FakeBackend())["inference_ready"])


if __name__ == "__main__":
    unittest.main()
