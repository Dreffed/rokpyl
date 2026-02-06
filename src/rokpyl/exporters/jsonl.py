"""JSONL exporter."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from rokpyl.exporters.base import Exporter
from rokpyl.models.canonical import ConversationRecord


class JsonlExporter(Exporter):
    name = "jsonl"

    def write(self, records: List[ConversationRecord], options: dict | None = None) -> None:
        options = options or {}
        path = options.get("path")
        if not path:
            raise ValueError("jsonl exporter requires 'path'")
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [json.dumps(asdict(record), ensure_ascii=True) for record in records]
        output_path.write_text("\n".join(lines), encoding="utf-8")
