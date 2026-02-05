import json
import unittest
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stdout

from chatingester.cli import main


class CliIntegrationTests(unittest.TestCase):
    def test_cli_writes_jsonl_output(self):
        fixture = Path(__file__).parent / "fixtures" / "claude_minimal.json"
        with TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "out.jsonl"
            buffer = StringIO()
            with redirect_stdout(buffer):
                result = main(
                    [
                        "--export-path",
                        str(fixture),
                        "--parser",
                        "claude",
                        "--out-jsonl",
                        str(out_path),
                    ]
                )

            self.assertEqual(result, 0)
            self.assertTrue(out_path.exists())
            lines = out_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            payload = json.loads(lines[0])
            self.assertEqual(payload["id"], "c1")


if __name__ == "__main__":
    unittest.main()
