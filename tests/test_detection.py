import unittest
from pathlib import Path

from chatingester.core.detection import select_importers
from chatingester.importers.base import Importer


class HighScoreImporter(Importer):
    name = "high"

    def discover_sources(self, export_path):
        return []

    def can_parse(self, source_path):
        return 0.9

    def parse(self, source_path, options=None):
        return []


class CloseScoreImporter(Importer):
    name = "close"

    def discover_sources(self, export_path):
        return []

    def can_parse(self, source_path):
        return 0.86

    def parse(self, source_path, options=None):
        return []


class LowScoreImporter(Importer):
    name = "low"

    def discover_sources(self, export_path):
        return []

    def can_parse(self, source_path):
        return 0.02

    def parse(self, source_path, options=None):
        return []


class DetectionTests(unittest.TestCase):
    def test_select_importers_picks_ties(self):
        selected = select_importers(
            [HighScoreImporter, CloseScoreImporter],
            Path("/tmp/fake.json"),
            min_confidence=0.1,
            tie_delta=0.05,
        )
        self.assertEqual({cls.name for cls in selected}, {"high", "close"})

    def test_select_importers_filters_low_confidence(self):
        selected = select_importers(
            [LowScoreImporter],
            Path("/tmp/fake.json"),
            min_confidence=0.1,
            tie_delta=0.05,
        )
        self.assertEqual(selected, [])


if __name__ == "__main__":
    unittest.main()
