from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Attachment:
    name: Optional[str] = None
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    url: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    role: str
    content: str
    created_at: Optional[str] = None
    attachments: List[Attachment] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationRecord:
    id: str
    title: str
    platform: str
    project: Optional[str] = None
    date: Optional[str] = None
    summary: Optional[str] = None
    url: Optional[str] = None
    transcript: str = ""
    messages: List[Message] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
