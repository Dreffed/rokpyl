# Design

## Module Layout (Proposed)
```
src/chatingester/
  cli.py
  core/
    pipeline.py
    registry.py
    config.py
    errors.py
  models/
    canonical.py
  importers/
    base.py
    claude.py
    chatgpt.py
  exporters/
    base.py
    jsonl.py
    markdown.py
    notion.py
  summarizers/
    base.py
    ollama.py
plugins/
  local_importers/
  local_exporters/
```

## Interfaces
```python
class Importer:
    name: str
    def discover(self, root: Path) -> list[Path]: ...
    def can_parse(self, path: Path) -> float: ...
    def parse(self, path: Path, config: dict) -> list[ConversationRecord]: ...

class Exporter:
    name: str
    def write(self, records: list[ConversationRecord], config: dict) -> None: ...

class Summarizer:
    name: str
    def summarize(self, records: list[ConversationRecord], config: dict) -> list[ConversationRecord]: ...
```

## Config and Overrides
- Config precedence: defaults < config file < env vars < CLI flags.
- Support both auto-detect and explicit selection.

Example config (YAML):
```yaml
inputs:
  - path: /exports/claude.zip
    mode: auto
  - path: /exports/custom.json
    mode: explicit
    parser: my_custom_parser
    options:
      project: Research
outputs:
  - type: jsonl
    path: /output/conversations.jsonl
  - type: notion
    token_env: NOTION_TOKEN
    db_id_env: NOTION_DB_ID
summarize:
  enabled: true
  provider: ollama
  model: llama3.1:8b
```

## Detection Algorithm (Auto)
- Collect candidate files by extension and size.
- For each importer, call `can_parse(path)` and pick the highest score.
- If multiple scores are close, parse with multiple importers and dedupe.

## Normalization and Dedup
- Generate stable ID from platform ID, or hash of title+date+transcript.
- Deduplicate by stable ID, then URL.
- Generate transcript from messages using a canonical format.

## Error Handling
- Per-file failures do not stop the run.
- Per-record exporter failures are logged and skipped.
- Emit a summary report with counts and failures.

## Docker
- Use a slim Python base image.
- Mount `inputs/` and `output/`.
- Read secrets from env vars only.

