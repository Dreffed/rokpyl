# rokpyl

**Small stones, big archives.**

Convert AI chat exports into organized, searchable knowledge bases.

## Features

- 🔄 **Multi-format conversion** - Export to JSON, Markdown, HTML
- 📁 **Per-chat splitting** - Separate files for each conversation
- 🗄 **Graph database** - Neo4j integration for relationship mapping
- 📝 **Notion sync** - Automatic workspace updates
- 📊 **Smart summaries** - AI-powered conversation digests

## Quick Start
```bash
# Install
pip install rokpyl

# Convert exports
rokpyl convert exports/my-chats.json

# Full pipeline
rokpyl build exports/ --format json,md --graph --notion
```

## What rokpyl does

Takes messy AI chat exports and transforms them into:
-  Individual per-chat files (JSON, Markdown)
-  Graph database entries (relationships, topics)
-  Notion pages (organized workspaces)
-  Searchable archives (full-text indexing)

Like building a wall from small stones - one chat at a time.

## Usage

See [Documentation](https://rokpyl.readthedocs.io) for full guide.

## License

MIT  Your Name
