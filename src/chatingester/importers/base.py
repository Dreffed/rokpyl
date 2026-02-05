"""Importer base types."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, List

from chatingester.models.canonical import ConversationRecord


class Importer(ABC):
    name: str

    @abstractmethod
    def discover_sources(self, export_path: Path) -> List[Path]:
        raise NotImplementedError

    @abstractmethod
    def can_parse(self, source_path: Path) -> float:
        raise NotImplementedError

    @abstractmethod
    def parse(self, source_path: Path, options: dict | None = None) -> List[ConversationRecord]:
        raise NotImplementedError

    def iter_sources(self, export_path: Path) -> Iterable[Path]:
        return self.discover_sources(export_path)
