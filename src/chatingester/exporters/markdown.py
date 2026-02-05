"""Markdown exporter."""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from chatingester.exporters.base import Exporter
from chatingester.models.canonical import ConversationRecord


def _safe_name(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return cleaned or fallback


class MarkdownExporter(Exporter):
    name = "markdown"

    def write(self, records: List[ConversationRecord], options: dict | None = None) -> None:
        options = options or {}
        directory = options.get("dir")
        if not directory:
            raise ValueError("markdown exporter requires 'dir'")
        output_dir = Path(directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        for idx, record in enumerate(records, start=1):
            base = record.id or record.title or f"conversation_{idx}"
            filename = _safe_name(base, f"conversation_{idx}") + ".md"
            path = output_dir / filename
            contents = [
                f"# {record.title}",
                "",
                f"- Platform: {record.platform}",
                f"- Date: {record.date}",
                f"- ID: {record.id}",
                f"- URL: {record.url}",
                f"- Project: {record.project}",
                "",
            ]
            if record.summary:
                contents.extend(["## Summary", "", record.summary, ""])
            if record.transcript:
                contents.extend(["## Contents", "", record.transcript, ""])
            path.write_text("\n".join(contents), encoding="utf-8")
