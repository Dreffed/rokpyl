"""Pipeline orchestration."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Type

from chatingester.core.detection import select_importers
from chatingester.core.registry import ImporterRegistry
from chatingester.importers.base import Importer
from chatingester.models.canonical import ConversationRecord


class Pipeline:
    def __init__(self, registry: ImporterRegistry) -> None:
        self.registry = registry

    def run(self, config: Dict[str, Any]) -> List[ConversationRecord]:
        inputs = config.get("inputs", [])
        records: List[ConversationRecord] = []

        for entry in inputs:
            path = Path(entry["path"])
            mode = entry.get("mode", "auto")
            parser_name = entry.get("parser")
            options = entry.get("options") or {}

            if mode == "explicit" and parser_name:
                importer_cls = self.registry.get(parser_name)
                records.extend(self._parse_with(importer_cls, path, options))
                continue

            for importer_cls in self._select_importers(path):
                records.extend(self._parse_with(importer_cls, path, options))

        return records

    def _select_importers(self, path: Path) -> Iterable[Type[Importer]]:
        return select_importers(self.registry._importers.values(), path)

    def _parse_with(
        self, importer_cls: Type[Importer], path: Path, options: Dict[str, Any]
    ) -> List[ConversationRecord]:
        importer = importer_cls()
        records: List[ConversationRecord] = []
        for source in importer.discover_sources(path):
            records.extend(importer.parse(source, options))
        return records
