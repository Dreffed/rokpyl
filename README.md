# Chat Exporter → Notion

> Multi-Platform Chat Export Pipeline (Claude-first, extensible)

---

## Overview

This project provides a **pluggable exporter** that ingests chat export archives from AI chat platforms (starting with **Claude**, with support for others such as ChatGPT, Gemini, etc.), normalizes conversations into a canonical schema, optionally generates summaries, and synchronizes the results into a **Notion database** with **deduplication and update logic**.

It is designed for:

- Knowledge management
- Research archiving
- Audit / traceability of AI-assisted work
- Long-term indexing of conversations across platforms

---

## Key Features

- 🔌 **Pluggable parsers** (Claude-first, extensible)
- 🧱 **Canonical data model** across platforms
- 🧠 **Optional summarization** (local LLM via Ollama or other providers)
- 📄 **Local exports** (JSONL + optional Markdown)
- 🧭 **Notion sync** with:
  - Database discovery
  - Duplicate detection
  - Update vs create behavior
- 📚 **Large transcript safe** (automatic chunking for Notion limits)
- 🔁 **Idempotent re-runs** (safe to run repeatedly)

---

## Supported Platforms

| Platform | Status |
| -------- | -------- |
| Claude | ✅ Primary target |
| ChatGPT | 🔄 Reference implementation |
| Gemini | 🧩 Planned |
| Other bots | 🧩 Via plugin |

---

## High-Level Flow

```text
Export Archive
   ↓
Platform Parser (ClaudeParser, etc.)
   ↓
Canonical Conversation Records
   ↓
Optional Summarization
   ↓
Local Outputs (JSONL / Markdown)
   ↓
Notion Database Sync
```

---

## Canonical Outputs

Each conversation is normalized into:

- Chat Title
- Platform
- Project (label)
- Date (ISO 8601)
- Summary (optional)
- URL (if available or templated)
- Full transcript (role-tagged)
- Structured messages
- Attachments + metadata

---

## Directory Structure

```text
src/chatingester/
  cli.py                # CLI entrypoint
  core/                 # Pipeline, registry, config, errors
  models/               # Canonical dataclasses
  importers/            # Platform parsers
  exporters/            # JSONL/Markdown/Notion/DB/Folder
  summarizers/          # Optional summary providers
plugins/                # Local-only plugin modules
docs/                   # ARCH/DESIGN/SPEC/TEST_PLAN/WORKFLOW
tests/
README.md
```

---

## Installation

### Requirements

- Python 3.10+
- (Optional) Ollama running locally for summaries
- Notion integration token (for sync)

### Clone & Setup

```bash
git clone <repo-url>
cd exporter
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # if used
```

> The project is designed to work with **stdlib only**. `requests` may be used if explicitly added.

---

## Notion Setup

1. Create a **Notion Integration**
2. Copy the **Integration Token**
3. Share your target database with the integration
4. Ensure the database has (or can accept) the following properties:

| Property Name | Type |
| ------------- | ----- |
| Chat Title | Title |
| Platform | Text or Select |
| Project | Text or Select |
| Date | Date |
| Summary | Text |
| URL | URL |
| Conversation ID | Text |
| Last Synced | Date (optional) |

---

## Usage

### Basic Export (Local Only)

```bash
python main.py   --export-path /path/to/claude-export   --out-jsonl conversations.jsonl
```

### Multiple Inputs (Auto-Detect)

```bash
python main.py   --export-path /exports/claude.zip   --export-path /exports/chatgpt   --auto-detect   --out-jsonl conversations.jsonl
```

### Explicit Parser Selection

```bash
python main.py   --export-path /exports/claude.zip   --parser claude   --export-path /exports/custom.json   --parser my_custom_parser   --out-jsonl conversations.jsonl
```

### Export + Markdown

```bash
python main.py   --export-path /path/to/claude-export   --out-jsonl conversations.jsonl   --out-md-dir chats_md
```

### Export + Summarization

```bash
python main.py   --export-path /path/to/claude-export   --ollama-summary   --ollama-model llama3.1:8b
```

---

## Notion Sync

### Environment Variables (Recommended)

```bash
export NOTION_TOKEN="secret_xxx"
export NOTION_DB_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

### Sync to Notion

```bash
python main.py   --export-path /path/to/claude-export   --notion-sync   --project "Research / EA"
```

### Sync with URL Template

```bash
python main.py   --export-path /path/to/export   --notion-sync   --url-template "https://chat.example.com/c/{id}"
```

### Update Existing Pages (Append Snapshot)

```bash
python main.py   --export-path /path/to/export   --notion-sync   --notion-update-contents
```

---

## Deduplication Logic

Pages are matched in this order:

1. **Conversation ID** (preferred, stable)
2. **URL** (fallback)

On re-run:

- Existing pages are **updated**
- New conversations are **created**
- No duplicates are introduced

---

## Parser Design

Each platform parser must implement:

```python
discover_sources(export_path) -> list[Path]
parse(source_path) -> list[ConversationRecord]
```

All outputs must map to the canonical schema in `model.py`.

### Dynamic Detection vs Explicit Parser Selection
- Auto-detect: scan inputs and select the best parser by schema hints.
- Explicit: user can target specific files and parser names to bypass detection.
- Hybrid: explicit overrides + auto-detection for remaining files.

---

## Error Handling

- File-level parse failures are logged and skipped
- Notion API failures are logged per conversation
- Export continues even if individual records fail
- Final summary reports:
  - Parsed
  - Created
  - Updated
  - Skipped
  - Failed

---

## Testing

Recommended tests:

- ID stability
- Transcript generation
- Chunking logic for large transcripts
- Deduplication index correctness
- Notion sync dry-runs

---

## Roadmap Ideas

- Native Claude HTML export support
- Gemini parser
- Rich block rendering (code, tables)
- Replace vs append content strategy
- Bi-directional Notion updates
- Search-based incremental sync

---

## License

Internal / private by default.
Add a license if you plan to distribute.

---

## Related Docs

- `docs/ARCH.md` – System architecture and plugin strategy
- `docs/CONFIG.md` – Config file format and precedence
- `docs/DESIGN.md` – Module layout and interfaces
- `docs/SPEC.md` – Full technical specification
- `docs/TEST_PLAN.md` – Test strategy and coverage map
- `docs/WORKFLOW.md` – ARCH → Design → SPEC → TDD → test → deploy flow

## Config Examples

- `configs/default.yaml`
- `configs/local.example.yaml`

Use `configs/local.example.yaml` as a template and save your local overrides to
`configs/local.yaml` (ignored by git) to avoid committing secrets.
