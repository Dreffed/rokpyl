import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from chatingester.importers.claude import ClaudeImporter


class ClaudeImporterTests(unittest.TestCase):
    def test_can_parse_scores(self):
        importer = ClaudeImporter()
        self.assertGreater(importer.can_parse(Path("claude_export.json")), 0.5)
        self.assertGreater(importer.can_parse(Path("export.json")), 0.1)
        self.assertEqual(importer.can_parse(Path("notes.txt")), 0.0)

    def test_discover_sources(self):
        importer = ClaudeImporter()
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "a.json").write_text("{}", encoding="utf-8")
            (root / "b.txt").write_text("x", encoding="utf-8")
            (root / "c.html").write_text("<html></html>", encoding="utf-8")

            sources = importer.discover_sources(root)
            names = {path.name for path in sources}

            self.assertEqual(names, {"a.json", "c.html"})


if __name__ == "__main__":
    unittest.main()
