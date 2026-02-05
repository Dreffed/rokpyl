"""Pipeline orchestration."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Type

from chatingester.core.detection import select_importers
from chatingester.core.normalize import normalize_records
from chatingester.core.registry import ExporterRegistry, ImporterRegistry
from chatingester.importers.base import Importer
from chatingester.models.canonical import ConversationRecord


class Pipeline:
    def __init__(
        self, importer_registry: ImporterRegistry, exporter_registry: ExporterRegistry
    ) -> None:
        self.importer_registry = importer_registry
        self.exporter_registry = exporter_registry

    def run(self, config: Dict[str, Any]) -> List[ConversationRecord]:
        inputs = config.get("inputs", [])
        records: List[ConversationRecord] = []

        for entry in inputs:
            path = Path(entry["path"])
            mode = entry.get("mode", "auto")
            parser_name = entry.get("parser")
            options = entry.get("options") or {}

            if mode == "explicit" and parser_name:
                importer_cls = self.importer_registry.get(parser_name)
                records.extend(self._parse_with(importer_cls, path, options))
                continue

            for importer_cls in self._select_importers(path):
                records.extend(self._parse_with(importer_cls, path, options))

        records = normalize_records(records)
        self._run_exporters(records, config.get("outputs", []))
        return records

    def _select_importers(self, path: Path) -> Iterable[Type[Importer]]:
        return select_importers(self.importer_registry._importers.values(), path)

    def _parse_with(
        self, importer_cls: Type[Importer], path: Path, options: Dict[str, Any]
    ) -> List[ConversationRecord]:
        importer = importer_cls()
        records: List[ConversationRecord] = []
        for source in importer.discover_sources(path):
            records.extend(importer.parse(source, options))
        return records

    def _run_exporters(self, records: List[ConversationRecord], outputs: List[Dict[str, Any]]) -> None:
        for output in outputs:
            exporter_type = output.get("type")
            if not exporter_type:
                continue
            exporter_cls = self.exporter_registry.get(exporter_type)
            exporter = exporter_cls()
            exporter.write(records, output)
