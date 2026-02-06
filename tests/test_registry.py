import unittest

from rokpyl.core.registry import ImporterRegistry
from rokpyl.importers.base import Importer


class FakeImporter(Importer):
    name = "fake"

    def discover_sources(self, export_path):
        return []

    def can_parse(self, source_path):
        return 0.0

    def parse(self, source_path, options=None):
        return []


class RegistryTests(unittest.TestCase):
    def test_register_and_get(self):
        registry = ImporterRegistry()
        registry.register(FakeImporter)
        self.assertIs(registry.get("fake"), FakeImporter)

    def test_register_duplicate_raises(self):
        registry = ImporterRegistry()
        registry.register(FakeImporter)
        with self.assertRaises(ValueError):
            registry.register(FakeImporter)

    def test_register_missing_name_raises(self):
        class NamelessImporter(FakeImporter):
            name = ""

        registry = ImporterRegistry()
        with self.assertRaises(ValueError):
            registry.register(NamelessImporter)


if __name__ == "__main__":
    unittest.main()
