import unittest

from rokpyl.exporters.notion import NotionExporter
from rokpyl.models.canonical import ConversationRecord


class NotionExporterTests(unittest.TestCase):
    def test_dry_run_noop(self):
        exporter = NotionExporter()
        record = ConversationRecord(id="1", title="Demo", platform="Claude")
        exporter.write([record], {"dry_run": True})

    def test_non_dry_run_raises(self):
        exporter = NotionExporter()
        record = ConversationRecord(id="1", title="Demo", platform="Claude")
        with self.assertRaises(NotImplementedError):
            exporter.write([record], {"dry_run": False})


if __name__ == "__main__":
    unittest.main()
