"""Markdown exporter."""
from __future__ import annotations

import ast
import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import List

from rokpyl.exporters.base import Exporter
from rokpyl.models.canonical import ConversationRecord


def _safe_name(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return cleaned or fallback


def _extract_text(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(str(part) for part in value if part is not None)
    if isinstance(value, dict):
        if "text" in value:
            return str(value.get("text") or "")
        if "thinking" in value:
            return str(value.get("thinking") or "")
        if "value" in value:
            return str(value.get("value") or "")
        if "parts" in value and isinstance(value.get("parts"), list):
            return "\n".join(str(part) for part in value.get("parts") if part is not None)
    return str(value)


def _try_parse_json_text(value: str) -> object | None:
    stripped = value.strip()
    if not stripped or (not stripped.startswith("{") and not stripped.startswith("[")):
        return None
    try:
        return json.loads(stripped)
    except Exception:
        try:
            parsed = ast.literal_eval(stripped)
            if isinstance(parsed, (dict, list)):
                return parsed
        except Exception:
            return None
    return None


def _format_key_value(label: str, value: object) -> List[str]:
    if value is None or value == "":
        return []
    if isinstance(value, (dict, list)):
        return [
            f"- {label}:",
            "```json",
            json.dumps(value, indent=2, ensure_ascii=True),
            "```",
        ]
    return [f"- {label}: {value}"]


def _format_message(message) -> List[str]:
    lines: List[str] = []
    lines.extend(_format_key_value("Time", getattr(message, "created_at", None)))
    if getattr(message, "attachments", None):
        lines.extend(_format_key_value("Attachments", len(message.attachments)))

    content = message.content
    parsed = None
    if isinstance(content, str):
        parsed = _try_parse_json_text(content)
    if isinstance(content, (dict, list)):
        parsed = content

    def _format_parsed_dict(parsed_dict: dict) -> List[str]:
        block: List[str] = []
        text_keys = {"text", "thinking", "value", "parts"}
        for key in sorted(parsed_dict.keys()):
            if key in text_keys:
                continue
            block.extend(_format_key_value(key, parsed_dict.get(key)))

        for key in sorted(text_keys):
            if key not in parsed_dict:
                continue
            text = _extract_text(parsed_dict.get(key))
            if text.strip():
                block.append("")
                block.append(f"#### {key}")
                block.append("")
                block.append(text)
        block.extend(
            [
                "",
                "#### Segment JSON",
                "```json",
                json.dumps(parsed_dict, indent=2, ensure_ascii=True),
                "```",
            ]
        )
        return block

    if isinstance(parsed, dict):
        lines.extend(_format_parsed_dict(parsed))
        return lines

    if isinstance(parsed, list):
        for idx, item in enumerate(parsed, start=1):
            if isinstance(item, dict):
                lines.extend(_format_key_value("Segment", idx))
                lines.extend(_format_parsed_dict(item))
                lines.append("")
            else:
                text = _extract_text(item)
                if text.strip():
                    lines.extend(_format_key_value("Segment", idx))
                    lines.append("")
                    lines.append(text)
                    lines.append("")
        return lines

    text = _extract_text(content)
    if text.strip():
        lines.append("")
        lines.append(text)
        return lines

    if isinstance(content, (dict, list)):
        payload = json.dumps(content, indent=2, ensure_ascii=True)
        return lines + ["", "```json", payload, "```"]
    return lines


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
            if record.messages:
                contents.append("## Messages")
                contents.append("")
                for message in record.messages:
                    contents.append(f"### {message.role}")
                    contents.append("")
                    contents.extend(_format_message(message))
                    contents.append("")
            elif record.transcript:
                contents.extend(["## Contents", "", record.transcript, ""])
            contents.extend(
                [
                    "## Raw JSON",
                    "",
                    "```json",
                    json.dumps(asdict(record), indent=2, ensure_ascii=True),
                    "```",
                    "",
                ]
            )
            path.write_text("\n".join(contents), encoding="utf-8")
