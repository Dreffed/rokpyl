"""Importer registry."""
from __future__ import annotations

from typing import Dict, List, Type

from rokpyl.importers.base import Importer
from rokpyl.exporters.base import Exporter


class ImporterRegistry:
    def __init__(self) -> None:
        self._importers: Dict[str, Type[Importer]] = {}

    def register(self, importer_cls: Type[Importer]) -> None:
        name = getattr(importer_cls, "name", None)
        if not name:
            raise ValueError("Importer must define a non-empty name")
        if name in self._importers:
            raise ValueError(f"Importer already registered: {name}")
        self._importers[name] = importer_cls

    def get(self, name: str) -> Type[Importer]:
        try:
            return self._importers[name]
        except KeyError as exc:
            raise KeyError(f"Unknown importer: {name}") from exc

    def list_names(self) -> List[str]:
        return sorted(self._importers.keys())


class ExporterRegistry:
    def __init__(self) -> None:
        self._exporters: Dict[str, Type[Exporter]] = {}

    def register(self, exporter_cls: Type[Exporter]) -> None:
        name = getattr(exporter_cls, "name", None)
        if not name:
            raise ValueError("Exporter must define a non-empty name")
        if name in self._exporters:
            raise ValueError(f"Exporter already registered: {name}")
        self._exporters[name] = exporter_cls

    def get(self, name: str) -> Type[Exporter]:
        try:
            return self._exporters[name]
        except KeyError as exc:
            raise KeyError(f"Unknown exporter: {name}") from exc

    def list_names(self) -> List[str]:
        return sorted(self._exporters.keys())
