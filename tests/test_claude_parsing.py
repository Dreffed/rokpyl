import json
import unittest
from dataclasses import asdict
from pathlib import Path

from chatingester.importers.claude import ClaudeImporter


class ClaudeParsingTests(unittest.TestCase):
    def test_parse_minimal_fixture(self):
        root = Path(__file__).parent / "fixtures"
        source = root / "claude_minimal.json"
        expected = json.loads((root / "claude_minimal.jsonl").read_text(encoding="utf-8"))

        importer = ClaudeImporter()
        records = importer.parse(source, options={"project": None, "platform": "Claude"})

        self.assertEqual(len(records), 1)
        actual = asdict(records[0])
        self.assertEqual(actual, expected)

    def test_parse_minimal_jsonl_fixture(self):
        root = Path(__file__).parent / "fixtures"
        source = root / "claude_minimal_input.jsonl"
        expected = json.loads((root / "claude_minimal.jsonl").read_text(encoding="utf-8"))

        importer = ClaudeImporter()
        records = importer.parse(source, options={"project": None, "platform": "Claude"})

        self.assertEqual(len(records), 1)
        actual = asdict(records[0])
        self.assertEqual(actual, expected)

    def test_parse_jsonl_with_blanks_and_comments(self):
        root = Path(__file__).parent / "fixtures"
        source = root / "claude_minimal_with_blanks.jsonl"
        expected = json.loads((root / "claude_minimal.jsonl").read_text(encoding="utf-8"))

        importer = ClaudeImporter()
        records = importer.parse(source, options={"project": None, "platform": "Claude"})

        self.assertEqual(len(records), 1)
        actual = asdict(records[0])
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
