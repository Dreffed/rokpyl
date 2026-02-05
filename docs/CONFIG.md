# Config Specification

## Overview
Configuration is optional. CLI flags always override config values.

Precedence:
1) Defaults
2) Config file
3) Environment variables
4) CLI flags

## File Format
- YAML recommended.
- JSON is acceptable if needed.

## Top-Level Keys
```yaml
inputs: []
outputs: []
summarize: {}
notion: {}
project: null
platform: null
```

## Inputs
```yaml
inputs:
  - path: /exports/claude.zip
    mode: auto            # auto | explicit | hybrid
    parser: claude         # required if mode is explicit
    options:
      project: Research
      platform: Claude
  - path: /exports/custom.json
    mode: explicit
    parser: my_custom_parser
```

Notes:
- `mode: auto` uses schema detection to pick a parser.
- `mode: explicit` uses the specified parser and skips detection.
- `mode: hybrid` honors explicit fields, then auto-detects remaining files.

## Outputs
```yaml
outputs:
  - type: jsonl
    path: /output/conversations.jsonl
  - type: markdown
    dir: /output/chats_md
  - type: notion
    token_env: NOTION_TOKEN
    db_id_env: NOTION_DB_ID
    update_contents: false
  - type: folder
    dir: /output/raw
  - type: database
    url_env: DB_URL
```

## Summarization
```yaml
summarize:
  enabled: true
  provider: ollama
  model: llama3.1:8b
  host: http://localhost:11434
  timeout_s: 60
```

## Notion (Defaults)
```yaml
notion:
  token_env: NOTION_TOKEN
  db_id_env: NOTION_DB_ID
  db_name: null
  update_contents: false
  chunk_size: 1800
  properties:
    title: Chat Title
    platform: Platform
    project: Project
    date: Date
    summary: Summary
    url: URL
    conversation_id: Conversation ID
    last_synced: Last Synced
```

## Global Defaults
```yaml
project: null
platform: null
```

