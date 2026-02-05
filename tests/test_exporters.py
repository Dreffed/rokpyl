import json
import unittest
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

from chatingester.exporters.jsonl import JsonlExporter
from chatingester.exporters.markdown import MarkdownExporter
from chatingester.models.canonical import ConversationRecord, Message


class ExporterTests(unittest.TestCase):
    def test_jsonl_exporter_writes_records(self):
        record = ConversationRecord(
            id="1",
            title="Demo",
            platform="Claude",
            messages=[Message(role="user", content="Hi")],
            transcript="user: Hi",
        )
        with TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "out.jsonl"
            exporter = JsonlExporter()
            exporter.write([record], {"path": str(out_path)})

            lines = out_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            payload = json.loads(lines[0])
            self.assertEqual(payload["id"], "1")
            self.assertEqual(payload["transcript"], "user: Hi")

    def test_markdown_exporter_writes_files(self):
        record = ConversationRecord(
            id="abc",
            title="Demo",
            platform="Claude",
            messages=[Message(role="user", content="Hi")],
            transcript="user: Hi",
        )
        with TemporaryDirectory() as tmpdir:
            exporter = MarkdownExporter()
            exporter.write([record], {"dir": tmpdir})

            output_files = list(Path(tmpdir).glob("*.md"))
            self.assertEqual(len(output_files), 1)
            contents = output_files[0].read_text(encoding="utf-8")
            self.assertIn("# Demo", contents)
            self.assertIn("## Contents", contents)


if __name__ == "__main__":
    unittest.main()
