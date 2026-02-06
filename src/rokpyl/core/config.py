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


def _parse_path(key: str) -> List[str | int]:
    parts: List[str | int] = []
    buffer = ""
    idx_buffer = ""
    in_index = False

    for char in key:
        if char == "." and not in_index:
            if buffer:
                parts.append(buffer)
                buffer = ""
            continue
        if char == "[":
            if buffer:
                parts.append(buffer)
                buffer = ""
            in_index = True
            idx_buffer = ""
            continue
        if char == "]" and in_index:
            if not idx_buffer.isdigit():
                raise ConfigError(f"Invalid list index in key: {key}")
            parts.append(int(idx_buffer))
            in_index = False
            continue
        if in_index:
            idx_buffer += char
        else:
            buffer += char

    if in_index:
        raise ConfigError(f"Unclosed list index in key: {key}")
    if buffer:
        parts.append(buffer)
    return parts


def set_by_path(config: Dict[str, Any], path: Iterable[str | int], value: Any) -> None:
    current: Any = config
    parts = list(path)
    for part in parts[:-1]:
        if isinstance(part, int):
            if not isinstance(current, list):
                raise ConfigError("List index used on non-list container")
            while len(current) <= part:
                current.append({})
            current = current[part]
            continue
        if part not in current or not isinstance(current[part], (dict, list)):
            current[part] = {}
        current = current[part]
    last = parts[-1]
    if isinstance(last, int):
        if not isinstance(current, list):
            raise ConfigError("List index used on non-list container")
        while len(current) <= last:
            current.append(None)
        current[last] = value
        return
    current[last] = value


def parse_set_values(pairs: Iterable[str]) -> Dict[Tuple[str | int, ...], str]:
    values: Dict[Tuple[str | int, ...], str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ConfigError(f"Invalid --set value: {pair}")
        key, value = pair.split("=", 1)
        parts = _parse_path(key)
        if not parts:
            raise ConfigError(f"Invalid --set key: {pair}")
        values[tuple(parts)] = value
    return values


def apply_set_overrides(config: Dict[str, Any], pairs: Iterable[str]) -> Dict[str, Any]:
    result = dict(config)
    for path, value in parse_set_values(pairs).items():
        set_by_path(result, path, value)
    return result


def _parse_env_path(key: str) -> List[str | int]:
    parts: List[str | int] = []
    for segment in key.split("__"):
        if not segment:
            continue
        if segment.isdigit():
            parts.append(int(segment))
        else:
            parts.append(segment.lower())
    return parts


def apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(config)
    prefix = "ROKPYL__"
    for env_key, value in os.environ.items():
        if not env_key.startswith(prefix):
            continue
        path = _parse_env_path(env_key[len(prefix) :])
        if not path:
            continue
        set_by_path(result, path, value)
    return result
