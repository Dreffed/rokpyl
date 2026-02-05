"""Normalization helpers."""
from __future__ import annotations

import hashlib
from typing import List

from chatingester.models.canonical import ConversationRecord, Message


def _build_transcript(messages: List[Message]) -> str:
    lines = []
    for message in messages:
        role = message.role or "unknown"
        content = message.content or ""
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _stable_fallback_id(record: ConversationRecord) -> str:
    payload = "|".join(
        [
            record.platform or "",
            record.title or "",
            record.date or "",
            record.transcript or "",
        ]
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"auto_{digest[:16]}"


def normalize_records(records: List[ConversationRecord]) -> List[ConversationRecord]:
    for record in records:
        if not record.transcript and record.messages:
            record.transcript = _build_transcript(record.messages)
        if not record.id:
            record.id = _stable_fallback_id(record)

    seen_ids = set()
    seen_urls = set()
    deduped: List[ConversationRecord] = []

    for record in records:
        if record.id and record.id in seen_ids:
            continue
        if record.url and record.url in seen_urls:
            continue
        if record.id:
            seen_ids.add(record.id)
        if record.url:
            seen_urls.add(record.url)
        deduped.append(record)

    return deduped
