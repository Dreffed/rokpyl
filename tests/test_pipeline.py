import unittest
from pathlib import Path

from chatingester.core.pipeline import Pipeline
from chatingester.core.registry import ImporterRegistry
from chatingester.importers.base import Importer
from chatingester.models.canonical import ConversationRecord


class FakeImporter(Importer):
    name = "fake"

    def __init__(self) -> None:
        self.seen = []

    def discover_sources(self, export_path: Path):
        return [export_path]

    def can_parse(self, source_path: Path):
        return 1.0

    def parse(self, source_path: Path, options=None):
        self.seen.append((str(source_path), options))
        return [ConversationRecord(id="1", title="t", platform="p")]


class PipelineTests(unittest.TestCase):
    def test_pipeline_explicit_parser(self):
        registry = ImporterRegistry()
        registry.register(FakeImporter)
        pipeline = Pipeline(registry)

        records = pipeline.run(
            {"inputs": [{"path": "./data", "mode": "explicit", "parser": "fake"}]}
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].id, "1")


if __name__ == "__main__":
    unittest.main()
