"""CLI entrypoint for rokpyl."""
from __future__ import annotations

import argparse
from typing import Any, Dict, List, Tuple

from rokpyl.core.config import (
    ConfigError,
    apply_env_overrides,
    apply_set_overrides,
    load_config,
    merge_dicts,
)
from rokpyl.core.pipeline import Pipeline
from rokpyl.core.registry import ExporterRegistry, ImporterRegistry
from rokpyl.exporters.jsonl import JsonlExporter
from rokpyl.exporters.markdown import MarkdownExporter
from rokpyl.exporters.notion import NotionExporter
from rokpyl.importers.claude import ClaudeImporter
from rokpyl.importers.chatgpt import ChatGptImporter


def parse_inputs(args: argparse.Namespace) -> List[Dict[str, Any]]:
    inputs: List[Dict[str, Any]] = []
    for path, parser_name in args.inputs:
        entry: Dict[str, Any] = {"path": path}
        if parser_name:
            entry["mode"] = "explicit"
            entry["parser"] = parser_name
        else:
            entry["mode"] = "auto" if args.auto_detect else "explicit"
        inputs.append(entry)
    return inputs


def build_config(args: argparse.Namespace) -> Dict[str, Any]:
    config = load_config(args.config)
    config = apply_env_overrides(config)
    config = apply_set_overrides(config, args.set_values or [])

    if args.project:
        config = merge_dicts(config, {"project": args.project})
    if args.platform:
        config = merge_dicts(config, {"platform": args.platform})

    if args.inputs:
        config = merge_dicts(config, {"inputs": parse_inputs(args)})

    outputs: List[Dict[str, Any]] = []
    if args.out_jsonl:
        outputs.append({"type": "jsonl", "path": args.out_jsonl})
    if args.out_md_dir:
        outputs.append({"type": "markdown", "dir": args.out_md_dir})
    if outputs:
        config = merge_dicts(config, {"outputs": outputs})

    return config


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="rokpyl CLI")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--set", dest="set_values", action="append")

    parser.add_argument("--export-path", dest="export_path", action="append")
    parser.add_argument("--input", dest="input_path", action="append")
    parser.add_argument("--parser", dest="parser_name", action="append")
    parser.add_argument("--auto-detect", action="store_true")

    parser.add_argument("--out-jsonl")
    parser.add_argument("--out-md-dir")
    parser.add_argument("--platform")
    parser.add_argument("--project")

    args = parser.parse_args(argv)

    paths = (args.export_path or []) + (args.input_path or [])
    parsers = args.parser_name or []

    inputs: List[Tuple[str, str | None]] = []
    for idx, path in enumerate(paths):
        parser_name = parsers[idx] if idx < len(parsers) else None
        inputs.append((path, parser_name))
    args.inputs = inputs
    return args


def build_registry() -> ImporterRegistry:
    registry = ImporterRegistry()
    registry.register(ClaudeImporter)
    registry.register(ChatGptImporter)
    return registry

def build_exporter_registry() -> ExporterRegistry:
    registry = ExporterRegistry()
    registry.register(JsonlExporter)
    registry.register(MarkdownExporter)
    registry.register(NotionExporter)
    return registry


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = build_config(args)
    except ConfigError as exc:
        raise SystemExit(str(exc))

    if not config.get("inputs"):
        raise SystemExit("No inputs provided; use --export-path or --input")

    registry = build_registry()
    exporter_registry = build_exporter_registry()
    pipeline = Pipeline(registry, exporter_registry)
    records = pipeline.run(config)

    print(
        "Run complete: inputs={inputs} records={records}".format(
            inputs=len(config.get("inputs", [])),
            records=len(records),
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
