# Architecture

## Goals
- Ingest chat exports from zip files or folders.
- Support dynamic schema detection and explicit parser selection.
- Normalize to a canonical model for consistent downstream processing.
- Provide pluggable exporters (local JSONL, Markdown, Notion, database, folder).
- Run locally or in Docker with minimal dependencies.

## Constraints
- Prefer Python stdlib; only add third-party deps when justified.
- Local plugins only (no package registry/entry points yet).
- Defensive parsing for evolving export formats.

## System Overview
```
Inputs (zip/folder)
  -> Discovery + Selection (auto-detect or explicit)
  -> Importers (platform parsers)
  -> Normalization + Dedup
  -> Optional Summarization
  -> Exporters (JSONL/MD/Notion/DB/Folder)
```

## Components
- CLI/Orchestrator: reads config/flags, selects importers/exporters, runs pipeline.
- Importers: parse platform exports into canonical records.
- Normalizer: merges sources, fills defaults, generates transcript and stable IDs.
- Summarizer: optional summary provider (e.g., Ollama).
- Exporters: local file outputs + Notion sync + future DB/folder sinks.
- Registry: local registry of importers/exporters with explicit overrides.

## Input Discovery and Selection
- Auto mode:
  - Recursively scan export roots.
  - Score candidates by file extension, known markers, and JSON schema hints.
  - Allow multiple importers to run if confidence is similar.
- Explicit mode:
  - User provides file paths and parser names directly.
  - Skip auto-detection for those inputs.
- Hybrid:
  - Explicit overrides are honored; remaining files are auto-detected.

## Plugin Strategy (Local Only)
- Importers/exporters live in the repo under `src/chatingester/*`.
- Optional `plugins/` directory for local custom modules.
- Registry resolves by name to local modules only.

## Deployment
- Docker image runs the CLI, mounts input/output volumes, uses env vars for secrets.

