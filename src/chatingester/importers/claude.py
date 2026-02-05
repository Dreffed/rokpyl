"""Claude importer skeleton."""
from __future__ import annotations

from pathlib import Path
import json
from typing import List

from chatingester.importers.base import Importer
from chatingester.models.canonical import ConversationRecord, Message


class ClaudeImporter(Importer):
    name = "claude"

    def discover_sources(self, export_path: Path) -> List[Path]:
        if export_path.is_file():
            return [export_path]
        if not export_path.exists():
            return []
        return [
            path
            for path in export_path.rglob("*")
            if path.is_file()
            and path.suffix.lower() in {".json", ".jsonl", ".html", ".csv", ".zip"}
        ]

    def can_parse(self, source_path: Path) -> float:
        name = source_path.name.lower()
        if "claude" in name:
            return 0.6
        if source_path.suffix.lower() in {".json", ".jsonl"}:
            return 0.2
        return 0.0

    def parse(
        self, source_path: Path, options: dict | None = None
    ) -> List[ConversationRecord]:
        options = options or {}
        suffix = source_path.suffix.lower()
        if suffix not in {".json", ".jsonl"}:
            return []

        records: List[ConversationRecord] = []
        platform = options.get("platform") or "Claude"
        project = options.get("project")

        if suffix == ".jsonl":
            for line in source_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                payload = json.loads(line)
                records.extend(
                    self._parse_payload(payload, platform=platform, project=project)
                )
            return records

        payload = json.loads(source_path.read_text(encoding="utf-8"))
        return self._parse_payload(payload, platform=platform, project=project)

    def _parse_payload(
        self, payload: dict, *, platform: str, project: str | None
    ) -> List[ConversationRecord]:
        conversations = payload.get("conversations")
        if conversations is None and isinstance(payload, list):
            conversations = payload
        if conversations is None:
            conversations = [payload]

        records: List[ConversationRecord] = []
        for convo in conversations:
            messages: List[Message] = []
            transcript_lines: List[str] = []
            for message in convo.get("messages", []):
                role = message.get("role") or "unknown"
                content = message.get("content") or ""
                messages.append(Message(role=role, content=content))
                transcript_lines.append(f"{role}: {content}")

            records.append(
                ConversationRecord(
                    id=str(convo.get("id") or ""),
                    title=str(convo.get("title") or "Untitled conversation"),
                    platform=platform,
                    project=project,
                    date=convo.get("date"),
                    transcript="\n".join(transcript_lines),
                    messages=messages,
                )
            )

        return records
