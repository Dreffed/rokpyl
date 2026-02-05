"""ChatGPT exporter parser (minimal)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from chatingester.importers.base import Importer
from chatingester.models.canonical import ConversationRecord, Message


def _to_iso(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, str):
        return value
    return None


class ChatGptImporter(Importer):
    name = "chatgpt"

    def discover_sources(self, export_path: Path) -> List[Path]:
        if export_path.is_file():
            return [export_path]
        if not export_path.exists():
            return []
        return [
            path
            for path in export_path.rglob("*")
            if path.is_file()
            and path.suffix.lower() in {".json", ".jsonl", ".zip"}
        ]

    def can_parse(self, source_path: Path) -> float:
        name = source_path.name.lower()
        if "conversations" in name or "chatgpt" in name:
            return 0.7
        if source_path.suffix.lower() in {".json", ".jsonl"}:
            return 0.2
        return 0.0

    def parse(self, source_path: Path, options: dict | None = None) -> List[ConversationRecord]:
        options = options or {}
        suffix = source_path.suffix.lower()
        if suffix not in {".json", ".jsonl"}:
            return []

        platform = options.get("platform") or "ChatGPT"
        project = options.get("project")

        if suffix == ".jsonl":
            records: List[ConversationRecord] = []
            for line in source_path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                payload = json.loads(stripped)
                records.extend(self._parse_payload(payload, platform=platform, project=project))
            return records

        payload = json.loads(source_path.read_text(encoding="utf-8"))
        return self._parse_payload(payload, platform=platform, project=project)

    def _parse_payload(
        self, payload, *, platform: str, project: str | None
    ) -> List[ConversationRecord]:
        conversations = payload
        if isinstance(payload, dict):
            conversations = payload.get("conversations", payload.get("items", payload))
        if isinstance(conversations, dict):
            conversations = [conversations]
        if not isinstance(conversations, list):
            return []

        records: List[ConversationRecord] = []
        for convo in conversations:
            mapping = convo.get("mapping") or {}
            messages: List[Message] = []

            for node in mapping.values():
                message = node.get("message") if isinstance(node, dict) else None
                if not message:
                    continue
                author = message.get("author") or {}
                role = author.get("role") or "unknown"
                content = message.get("content") or {}
                parts = content.get("parts") or []
                text = "\n".join(str(part) for part in parts if part is not None)
                created_at = _to_iso(message.get("create_time"))
                if text:
                    messages.append(Message(role=role, content=text, created_at=created_at))

            messages.sort(key=lambda msg: msg.created_at or "")
            transcript_lines = [f"{msg.role}: {msg.content}" for msg in messages]

            records.append(
                ConversationRecord(
                    id=str(convo.get("id") or ""),
                    title=str(convo.get("title") or "Untitled conversation"),
                    platform=platform,
                    project=project,
                    date=_to_iso(convo.get("create_time") or convo.get("update_time")),
                    transcript="\n".join(transcript_lines),
                    messages=messages,
                    metadata={},
                )
            )

        return records
