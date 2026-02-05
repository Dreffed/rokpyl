# SPEC.md
## Multi-Platform Chat Exporter → Notion
*(Claude-first, extensible to other chatbots)*

---

## 1. Purpose

Build a reusable exporter that ingests **chat export archives** from multiple chatbot platforms (starting with **Claude**, but extensible to others), normalizes chats into a common schema, optionally generates summaries, and syncs results into a **Notion database** with **deduplication and update** behavior.

---

## 2. Target Outcomes

For each conversation/chat in an export, the system must:

- Extract and normalize:
  - **Chat Title**
  - **Platform** (e.g., Claude, ChatGPT, Gemini)
  - **Project** (user-supplied label)
  - **Date** (best available timestamp)
  - **Summary** (optional; generated)
  - **URL** (if available or templated)
  - **Contents** (full transcript, role-tagged)
  - **Additional Metadata** (attachments, model info, tags, tool calls, etc.)

- Sync to Notion:
  - Create new pages for new conversations
  - Update existing pages if already present
  - Avoid duplicates using stable identifiers

---

## 3. Supported Inputs

### 3.1 Input Types
- Unzipped export directory (required)
- Zip archive (optional; may be unzipped to temp)

### 3.2 Export Discovery
The exporter must:
- Recursively scan the export directory
- Identify likely conversation files (JSON / JSONL / HTML / CSV)
- Support multiple source files in a single export
- Merge and deduplicate results

---

## 4. Claude Export Support

### 4.1 Parser Design
Implement a **ClaudeParser** that:
- Detects Claude-specific export structures
- Extracts conversations even when fields are missing or renamed
- Handles varied message formats and attachments

### 4.2 Parser Responsibilities
- Locate conversation objects
- Extract:
  - Conversation ID (or generate stable fallback)
  - Title (or “Untitled conversation”)
  - Timestamps (conversation-level or message-level)
  - Messages (role, content, timestamp)
  - Attachments (if any)
  - URL or permalink (if present)

---

## 5. Canonical Data Model

All platform parsers must map into the following canonical schema.

### 5.1 ConversationRecord

| Field | Type | Notes |
|-----|-----|------|
| id | string | Stable ID; platform ID preferred |
| title | string | Chat title |
| platform | string | e.g., “Claude” |
| project | string \| null | User-provided label |
| date | ISO 8601 \| null | Best available timestamp |
| summary | string \| null | Optional generated summary |
| url | string \| null | Permalink or templated |
| transcript | string | Full role-tagged transcript |
| messages | Message[] | Structured messages |
| metadata | object | Extra platform-specific data |

### 5.2 Message

| Field | Type |
|-----|-----|
| role | string |
| content | string |
| created_at | ISO 8601 \| null |
| attachments | Attachment[] |
| extra | object |

### 5.3 Attachment

| Field | Type |
|-----|-----|
| name | string \| null |
| mime_type | string \| null |
| size_bytes | number \| null |
| url | string \| null |
| extra | object |

---

## 6. Output Requirements

### 6.1 Local Outputs
- **JSONL**: one `ConversationRecord` per line
- Optional **Markdown files**, one per conversation:
  - Header: Title, Platform, Date, ID, URL, Project
  - Summary section (if available)
  - Contents section (full transcript)
  - Attachments roll-up

### 6.2 Notion Outputs
For each conversation:
- Database properties:
  - **Chat Title** (title)
  - **Platform**
  - **Project**
  - **Date**
  - **Summary**
  - **URL**
  - **Conversation ID**
  - *(Optional)* Last Synced
- Page body blocks:
  - Summary
  - Contents (chunked transcript)
  - Attachments (optional)

---

## 7. Notion Integration

### 7.1 Connectivity
- Notion REST API (v1)
- Auth via integration token

### 7.2 Database Discovery
- Prefer `--notion-db-id`
- Fallback: search by database name

### 7.3 Read Existing Records
- Query all pages (handle pagination)
- Build dedupe indices:
  - Primary: Conversation ID
  - Secondary: URL

### 7.4 Dedupe + Update Logic
- If record exists:
  - Update properties
  - Optionally append updated contents snapshot
- If record does not exist:
  - Create new page

### 7.5 Notion Limits
- Chunk text blocks to ~1,800 characters
- Avoid large single blocks
- Cap attachment listings (e.g., 50 items)

---

## 8. Summarization (Optional)

- Enabled via CLI flag
- Default provider: **Ollama**
- Summary must include:
  1. 1–2 sentence overview
  2. Key topics (≤ 8 bullets)
  3. Deliverables / decisions
  4. Follow-ups / next steps

---

## 9. URL Generation

- Use platform-provided URL if available
- Else allow a template:
