import unittest

from rokpyl.core.normalize import normalize_records
from rokpyl.models.canonical import ConversationRecord, Message


class NormalizeTests(unittest.TestCase):
    def test_transcript_and_id_fallback(self):
        record = ConversationRecord(
            id="",
            title="Demo",
            platform="Claude",
            messages=[Message(role="user", content="Hi")],
        )

        normalized = normalize_records([record])
        self.assertEqual(len(normalized), 1)
        self.assertTrue(normalized[0].id.startswith("auto_"))
        self.assertEqual(normalized[0].transcript, "user: Hi")

    def test_dedupe_by_id_then_url(self):
        a = ConversationRecord(id="1", title="A", platform="X", url="http://a")
        b = ConversationRecord(id="1", title="B", platform="X", url="http://b")
        c = ConversationRecord(id="2", title="C", platform="X", url="http://a")
        d = ConversationRecord(id="3", title="D", platform="X", url="http://d")

        normalized = normalize_records([a, b, c, d])
        self.assertEqual([r.id for r in normalized], ["1", "3"])

    def test_dedupe_by_url_when_ids_unique(self):
        a = ConversationRecord(id="1", title="A", platform="X", url="http://a")
        b = ConversationRecord(id="2", title="B", platform="X", url="http://a")

        normalized = normalize_records([a, b])
        self.assertEqual([r.id for r in normalized], ["1"])


if __name__ == "__main__":
    unittest.main()
