"""Exporter base types."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from rokpyl.models.canonical import ConversationRecord


class Exporter(ABC):
    name: str

    @abstractmethod
    def write(self, records: List[ConversationRecord], options: dict | None = None) -> None:
        raise NotImplementedError
