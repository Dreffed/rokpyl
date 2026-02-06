"""Detection helpers for importer selection."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Tuple, Type

from rokpyl.importers.base import Importer


def score_importer(importer_cls: Type[Importer], source_path: Path) -> float:
    try:
        importer = importer_cls()
        return float(importer.can_parse(source_path))
    except Exception:
        return 0.0


def select_importers(
    importers: Iterable[Type[Importer]],
    source_path: Path,
    *,
    min_confidence: float = 0.1,
    tie_delta: float = 0.05,
) -> List[Type[Importer]]:
    scored: List[Tuple[Type[Importer], float]] = [
        (importer_cls, score_importer(importer_cls, source_path))
        for importer_cls in importers
    ]
    if not scored:
        return []

    max_score = max(score for _, score in scored)
    if max_score < min_confidence:
        return []

    selected = [
        importer_cls
        for importer_cls, score in scored
        if max_score - score <= tie_delta
    ]
    return selected
