# Test Plan

## Objectives
- Validate importers handle real-world variations.
- Ensure canonical outputs are stable and deterministic.
- Prevent duplicates in Notion and local exports.
- Keep failures isolated to the smallest unit.

## Test Pyramid
- Unit tests: parser helpers, ID generation, transcript formatting, chunking.
- Integration tests: end-to-end pipeline on fixtures, Notion client mocked.
- E2E tests: CLI runs against sample exports in a temp workspace.

## Core Test Areas
- Input discovery:
  - Auto detection chooses expected importer.
  - Explicit parser selection bypasses detection.
- Canonical model:
  - Required fields present, optional fields handled gracefully.
  - Stable ID is deterministic across runs.
- Transcript generation:
  - Role tagging, ordering, newline handling.
- Chunking:
  - Notion chunk size boundaries and content preservation.
- Dedup logic:
  - ID takes precedence over URL.
  - No duplicate creates on rerun.
- Exporters:
  - JSONL output is one record per line.
  - Markdown headers include required metadata.
  - Notion exporter handles failures per record.

## Fixtures
- Minimal Claude export (single conversation).
- Mixed export with multiple files and attachments.
- Large transcript to trigger chunking.

## Tooling
- Prefer stdlib `unittest` or `pytest` if adopted later.
- Use golden fixtures for canonical JSONL output.

