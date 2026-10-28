import tempfile
import unittest
from pathlib import Path

from logicasofia.inventory import collect_inventory, read_linux_meminfo, read_cpu_model


class InventoryTests(unittest.TestCase):
    def test_memory_parsing(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "meminfo"
            path.write_text("MemTotal:       4096 kB\nMemFree: 2048 kB\n")
            self.assertEqual(read_linux_meminfo(str(path)), 4096 * 1024)

    def test_memory_missing(self):
        self.assertIsNone(read_linux_meminfo("/not/a/real/meminfo/path"))

    def test_cpu_model_parsing(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cpuinfo"
            path.write_text("processor : 0\nmodel name : Test CPU 42\n")
            self.assertEqual(read_cpu_model(str(path)), "Test CPU 42")

    def test_inventory_truthful_backend(self):
        doc = collect_inventory()
        self.assertFalse(doc["model_backend_configured"])
        self.assertIn("disk_root_free_bytes", doc)
        self.assertIn("logical_cpus", doc)


if __name__ == "__main__":
    unittest.main()
