import json
import os
import unittest
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stdout

from rokpyl.cli import main


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

    def test_cli_auto_detect(self):
        fixture = Path(__file__).parent / "fixtures" / "claude_minimal.json"
        with TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "out.jsonl"
            buffer = StringIO()
            with redirect_stdout(buffer):
                result = main(
                    [
                        "--export-path",
                        str(fixture),
                        "--auto-detect",
                        "--out-jsonl",
                        str(out_path),
                    ]
                )

            self.assertEqual(result, 0)
            self.assertTrue(out_path.exists())

    def test_cli_writes_markdown_output(self):
        fixture = Path(__file__).parent / "fixtures" / "claude_minimal.json"
        with TemporaryDirectory() as tmpdir:
            buffer = StringIO()
            with redirect_stdout(buffer):
                result = main(
                    [
                        "--export-path",
                        str(fixture),
                        "--parser",
                        "claude",
                        "--out-md-dir",
                        tmpdir,
                    ]
                )

            self.assertEqual(result, 0)
            output_files = list(Path(tmpdir).glob("*.md"))
            self.assertEqual(len(output_files), 1)
            contents = output_files[0].read_text(encoding="utf-8")
            self.assertIn("# Demo", contents)

    def test_cli_notion_dry_run(self):
        fixture = Path(__file__).parent / "fixtures" / "claude_minimal.json"
        with TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "inputs": [{"path": str(fixture), "mode": "explicit", "parser": "claude"}],
                        "outputs": [{"type": "notion", "dry_run": True}],
                    }
                ),
                encoding="utf-8",
            )
            buffer = StringIO()
            with redirect_stdout(buffer):
                result = main(
                    [
                        "--config",
                        str(config_path),
                    ]
                )

            self.assertEqual(result, 0)

    def test_cli_env_overrides(self):
        fixture = Path(__file__).parent / "fixtures" / "claude_minimal.json"
        with TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "out.jsonl"
            buffer = StringIO()
            env_key = "rokpyl__PROJECT"
            original = os.environ.get(env_key)
            os.environ[env_key] = "EnvProject"
            try:
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
            finally:
                if original is None:
                    os.environ.pop(env_key, None)
                else:
                    os.environ[env_key] = original

            self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
