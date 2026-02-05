"""Configuration loading and merging."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple


class ConfigError(RuntimeError):
    pass


def load_config(path: str | None) -> Dict[str, Any]:
    if not path:
        return {}
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    if config_path.suffix.lower() in {".json"}:
        return json.loads(config_path.read_text(encoding="utf-8"))

    if config_path.suffix.lower() in {".yml", ".yaml"}:
        try:
            import yaml  # type: ignore
        except Exception as exc:
            raise ConfigError(
                "YAML config requires PyYAML; install it or use JSON"
            ) from exc
        return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

    raise ConfigError("Unsupported config format; use .json or .yaml")


def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def set_by_path(config: Dict[str, Any], path: Iterable[str], value: Any) -> None:
    current = config
    parts = list(path)
    for part in parts[:-1]:
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]
    current[parts[-1]] = value


def parse_set_values(pairs: Iterable[str]) -> Dict[Tuple[str, ...], str]:
    values: Dict[Tuple[str, ...], str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ConfigError(f"Invalid --set value: {pair}")
        key, value = pair.split("=", 1)
        path = tuple(part for part in key.split(".") if part)
        if not path:
            raise ConfigError(f"Invalid --set key: {pair}")
        values[path] = value
    return values


def apply_set_overrides(config: Dict[str, Any], pairs: Iterable[str]) -> Dict[str, Any]:
    result = dict(config)
    for path, value in parse_set_values(pairs).items():
        set_by_path(result, path, value)
    return result


def apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    # Placeholder: env mapping will be defined with config schema.
    return config
