"""Infer a lightweight JSON schema from large files.

Supports JSON and JSONL inputs. Designed for large, unformatted exports.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "unknown"


def _empty_schema() -> Dict[str, Any]:
    return {
        "type_counts": {},
        "properties": {},
        "items": None,
        "examples": [],
    }


def _add_example(schema: Dict[str, Any], value: Any, max_examples: int) -> None:
    if len(schema["examples"]) >= max_examples:
        return
    if isinstance(value, (dict, list)):
        return
    schema["examples"].append(value)


def merge_schema(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    for name, count in source["type_counts"].items():
        target["type_counts"][name] = target["type_counts"].get(name, 0) + count

    for key, child in source["properties"].items():
        if key not in target["properties"]:
            target["properties"][key] = _empty_schema()
        merge_schema(target["properties"][key], child)

    if source["items"] is not None:
        if target["items"] is None:
            target["items"] = _empty_schema()
        merge_schema(target["items"], source["items"])

    for example in source["examples"]:
        _add_example(target, example, max_examples=5)

    return target


def infer_schema(value: Any, *, max_examples: int = 5) -> Dict[str, Any]:
    schema = _empty_schema()
    type_name = _type_name(value)
    schema["type_counts"][type_name] = 1
    _add_example(schema, value, max_examples)

    if isinstance(value, dict):
        for key, item in value.items():
            schema["properties"][key] = infer_schema(item, max_examples=max_examples)
    elif isinstance(value, list):
        items_schema = _empty_schema()
        for item in value:
            merge_schema(items_schema, infer_schema(item, max_examples=max_examples))
        schema["items"] = items_schema

    return schema


def infer_from_iter(values: Iterable[Any], *, max_items: int, max_examples: int) -> Dict[str, Any]:
    schema = _empty_schema()
    for idx, value in enumerate(values, start=1):
        merge_schema(schema, infer_schema(value, max_examples=max_examples))
        if idx >= max_items:
            break
    return schema


def _iter_jsonl(path: Path) -> Iterable[Any]:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        yield json.loads(stripped)


def extract_schema(path: Path, *, max_items: int, max_examples: int) -> Dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        return infer_from_iter(_iter_jsonl(path), max_items=max_items, max_examples=max_examples)

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return infer_from_iter(payload, max_items=max_items, max_examples=max_examples)
    return infer_schema(payload, max_examples=max_examples)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Infer a JSON schema from a file")
    parser.add_argument("path", help="Path to JSON or JSONL file")
    parser.add_argument("--out", help="Write schema to a file")
    parser.add_argument("--max-items", type=int, default=200, help="Max items to sample")
    parser.add_argument("--max-examples", type=int, default=5, help="Max scalar examples per node")
    args = parser.parse_args(argv)

    schema = extract_schema(Path(args.path), max_items=args.max_items, max_examples=args.max_examples)
    output = json.dumps(schema, indent=2, ensure_ascii=True)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
