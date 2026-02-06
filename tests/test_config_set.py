import unittest

from rokpyl.core.config import apply_set_overrides


class ConfigSetTests(unittest.TestCase):
    def test_set_list_index(self):
        base = {"outputs": []}
        updated = apply_set_overrides(
            base,
            [
                "outputs[0].type=jsonl",
                "outputs[0].path=/output/conversations.jsonl",
            ],
        )

        self.assertEqual(updated["outputs"][0]["type"], "jsonl")
        self.assertEqual(updated["outputs"][0]["path"], "/output/conversations.jsonl")


if __name__ == "__main__":
    unittest.main()
