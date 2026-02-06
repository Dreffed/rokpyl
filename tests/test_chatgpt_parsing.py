import json
import unittest
from dataclasses import asdict
from pathlib import Path

from rokpyl.importers.chatgpt import ChatGptImporter


class ChatGptParsingTests(unittest.TestCase):
    def test_parse_minimal_fixture(self):
        root = Path(__file__).parent / "fixtures"
        source = root / "chatgpt_minimal.json"
        expected = json.loads((root / "chatgpt_minimal.jsonl").read_text(encoding="utf-8"))

        importer = ChatGptImporter()
        records = importer.parse(source, options={"project": None, "platform": "ChatGPT"})

        self.assertEqual(len(records), 1)
        actual = asdict(records[0])
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
