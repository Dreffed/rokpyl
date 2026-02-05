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
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                payload = json.loads(stripped)
                records.extend(
                    self._parse_payload(payload, platform=platform, project=project)
                )
            return records

        payload = json.loads(source_path.read_text(encoding="utf-8"))
        return self._parse_payload(payload, platform=platform, project=project)

    def _parse_payload(
        self, payload: dict, *, platform: str, project: str | None
    ) -> List[ConversationRecord]:
        conversations = payload
        if isinstance(payload, dict):
            conversations = payload.get("conversations", payload)
        if isinstance(conversations, dict):
            conversations = [conversations]
        if not isinstance(conversations, list):
            conversations = [payload]

        records: List[ConversationRecord] = []
        for convo in conversations:
            messages: List[Message] = []
            transcript_lines: List[str] = []
            raw_messages = convo.get("chat_messages")
            if raw_messages is None:
                raw_messages = convo.get("messages", [])
            for message in raw_messages or []:
                role = message.get("role") or message.get("sender") or "unknown"
                if role == "human":
                    role = "user"
                content = message.get("content")
                if isinstance(content, dict):
                    content = content.get("text") or content.get("value")
                if content is None:
                    content = message.get("text") or ""
                messages.append(
                    Message(
                        role=role,
                        content=str(content),
                        created_at=message.get("created_at"),
                    )
                )
                transcript_lines.append(f"{role}: {content}")

            records.append(
                ConversationRecord(
                    id=str(convo.get("uuid") or convo.get("id") or ""),
                    title=str(
                        convo.get("name")
                        or convo.get("title")
                        or "Untitled conversation"
                    ),
                    platform=platform,
                    project=project,
                    date=convo.get("created_at") or convo.get("date") or convo.get("updated_at"),
                    summary=convo.get("summary"),
                    transcript="\n".join(transcript_lines),
                    messages=messages,
                )
            )

        return records
