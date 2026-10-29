# Aegis AI — System Architecture Document

**Version:** 0.4.0  
**Status:** Approved & Current Baseline  
**Date:** 2026-10-29  

---

## 1. Executive Summary

Aegis AI is a privacy-first, developer-centric personal AI operator and autonomous coding assistant built around three foundational pillars:
1. **Dual-Provider Inference with Strict Isolation**: Seamlessly switch between zero-data-leakage local inference via **Ollama** (`http://127.0.0.1:11434`) running **NVIDIA Nemotron 3.5 Bolt E4B** and high-throughput cloud inference via **Nebius Token Factory** or **OpenRouter** (`https://openrouter.ai/api/v1`). Under no circumstances is local code or conversation silently routed to the cloud.
2. **Human-in-the-Loop Security & Workspace Sandboxing**: All file modifications and shell executions are sandboxed inside `./workspace` (or configured `AEGIS_WORKSPACE`). Automatic timestamped backups are generated in `.aegis_backups/`, and every patch or allowlisted test runner command requires explicit human review and approval.
3. **ChatGPT-Inspired Premium Response Experience**: Obsidian-dark single-page interface with a zero-dependency multi-language syntax highlighter (12+ languages), resilient Markdown parsing (GFM tables, nested lists, blockquotes), safe URL sanitization, true client-side cancellation via `AbortController`, and one-click clipboard actions.

---

## 2. High-Level System Architecture Diagram

```
+-------------------------------------------------------------------------------------------------------+
|                                              BROWSER CLIENT                                           |
|                                                                                                       |
|  +---------------------------+  +-------------------------------+  +-------------------------------+  |
|  | Collapsible History       |  | Centered Reading Stream       |  | Response Experience Engine    |  |
|  | - Realtime Text Search    |  | - 48rem Focused Column        |  | - Zero-Dep Syntax Highlighting|  |
|  | - Date Grouping           |  | - Dynamic Message Composer    |  | - Safe Markdown & Tables     |  |
|  | - Mobile Off-Canvas Drawer|  | - Suggestion Starter Chips    |  | - Copy Actions & Toast System |  |
|  +---------------------------+  +-------------------------------+  | - AbortController (#btnStop)  |  |
|                                                                    +-------------------------------+  |
+-------------------------------------------------------------------------------------------------------+
                                                   |
                                                   | HTTP REST / JSON
                                                   v
+-------------------------------------------------------------------------------------------------------+
|                                           FASTAPI BACKEND SERVICE                                     |
|                                                                                                       |
|  API Routers:                                                                                         |
|  - /api/chat        -> Chat orchestrator, session history, memory injection, approval tag parser     |
|  - /api/provider    -> Runtime provider switching, connectivity health probes, model status tags      |
|  - /api/health      -> System readiness, DB connection, sanitized provider health probes              |
|  - /api/approvals   -> Human approval lifecycle engine (PROPOSED -> APPROVED -> EXECUTED)             |
|  - /api/workspace   -> Sandboxed workspace explorer, patch preview, unified diffs, backups            |
|  - /api/memory      -> Persistent SQLite semantic memory CRUD, keyword indexer, secret shield         |
|  - /api/projects    -> Project and task organization backlog                                          |
+-------------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+-------------------------------------------------------------------------------------------------------+
|                                         AGENT ORCHESTRATION LAYER                                     |
|                                                                                                       |
|  AgentService:                                                                                        |
|  1. Queries SQLite memory for keywords matching user prompt; filters sensitive secrets.               |
|  2. Injects system directives + active developer skill (Planner, Debugger, Explainer, Test Writer).   |
|  3. Snapshots active provider (settings.get_provider_snapshot()) to isolate concurrent sessions.       |
|  4. Dispatches request to LLMService.generate(messages, system_prompt, provider=snapshot).             |
|  5. Extracts <<<PROPOSE_PATCH>>>, <<<PROPOSE_COMMAND>>>, <<<PROPOSE_TASK>>> tags from response.       |
|  6. Writes pending approvals to SQLite with risk levels and diffs for user review.                   |
+-------------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+-------------------------------------------------------------------------------------------------------+
|                                         LLM PROVIDER ABSTRACTION                                      |
|                                                                                                       |
|  LLMService.generate(messages, system_prompt, provider=snapshot):                                     |
|                                                                                                       |
|        [provider == 'ollama']                                        [provider == 'cloud']            |
|                   |                                                             |                     |
|                   v                                                             v                     |
|         _generate_ollama()                                            _generate_cloud()               |
|     - POST {base_url}/api/chat                                    - Async OpenAI client               |
|     - HTTP timeouts (60s)                                         - Nebius Token Factory / OpenRouter |
|     - Handle 404 (model missing)                                  - Model ID fallback resilience      |
|     - Handle connection refusal                                   - Handle quota / auth errors        |
|                   |                                                             |                     |
|                   +------------------------------+------------------------------+                     |
|                                                  |                                                    |
|                                STRICT ISOLATION (ZERO SILENT FALLBACK)                                |
+-------------------------------------------------------------------------------------------------------+
            |                                                              |
            | HTTP (Localhost)                                             | HTTPS (Encrypted WAN)
            v                                                              v
+------------------------------------+                      +------------------------------------------+
|        Ollama Local Daemon         |                      |        Nebius Token Factory Cloud        |
|       http://127.0.0.1:11434       |                      |       https://openrouter.ai/api/v1       |
|    Model: nemotron-3.5-bolt:e4b    |                      |       Model: nvidia/nemotron-...         |
+------------------------------------+                      +------------------------------------------+
```

---

## 3. End-to-End Request Lifecycle

Tracing a complete request from the user's keystroke through to the final rendered UI:

1. **User Action**: The user enters a prompt into `#chatInput` and presses `Enter` (or clicks `#btnSend`).
2. **Client State Preparation**:
   - `frontend/app.js` checks if a request is already active; if so, returns early.
   - An `AbortController` instance is instantiated and stored in `currentAbortController`.
   - The UI updates: `#btnSend` hides, `#btnStop` reveals with an active pulse, `#composerStatus` announces processing.
   - A user message node is rendered into the chat container; the view scrolls to bottom.
3. **HTTP Dispatch**:
   - Client sends `POST /api/chat` with `{ message, conversation_id, project_id }` passing `{ signal: currentAbortController.signal }`.
4. **Backend Ingestion & Memory Enrichment**:
   - FastAPI `/api/chat` router passes payload to `AgentService.process_message()`.
   - `AgentService` queries SQLite `memories` table, performing keyword extraction on the user's prompt to find relevant contextual items.
   - Sensed secrets (passwords, tokens, credentials) are filtered out via `SecretShield`.
5. **Provider Snapshotting & Prompt Construction**:
   - `AgentService` grabs a thread-safe snapshot of the current inference provider (`settings.get_provider_snapshot()`).
   - The active developer skill (e.g., Debugger or Planner) injects its system persona and strict formatting directives.
   - The assembled context is forwarded to `LLMService.generate(messages, system_prompt, provider=snapshot)`.
6. **Inference Execution**:
   - If `provider == "ollama"`: Calls local Ollama daemon via `httpx.Client.post("http://127.0.0.1:11434/api/chat")`.
   - If `provider == "cloud"`: Calls Nebius Token Factory / OpenRouter via the OpenAI SDK.
   - If Ollama is offline or times out, an explicit sanitized operational error is returned. **Zero cloud fallback is executed.**
7. **Approval Tag Extraction**:
   - `AgentService` inspects the raw output for structured tags:
     - `<<<PROPOSE_PATCH:path>>>diff<<<END_PATCH>>>`
     - `<<<PROPOSE_COMMAND>>>cmd<<<END_COMMAND>>>`
     - `<<<PROPOSE_TASK:title>>>desc<<<END_TASK>>>`
   - For every detected tag, an approval record is persisted in SQLite with status `PENDING_APPROVAL`.
8. **HTTP Response & Client Rendering**:
   - Backend returns `{ reply, conversation_id, approvals: [...] }`.
   - `frontend/app.js` runs `renderSafeMarkdown(reply)`:
     - Fenced code blocks are isolated into `@@AEGIS-CODE-BLOCK-${idx}@@` placeholders.
     - Tables are converted into responsive HTML with `.msg-table-wrapper` horizontal scrollers.
     - Lists, headings, quotes, and inline styles are formatted.
     - Code placeholders are restored with syntax highlighting via `highlightSyntax(code, lang)`.
     - Code header chrome with language badge and copy button is injected.
   - Approval cards are rendered with interactive **Approve** and **Reject** buttons and unified diff viewers.
   - `#btnStop` hides, `#btnSend` returns, and `#composerStatus` resets.

---

## 4. Frontend Response Experience Architecture

### 4.1 Zero-Dependency Syntax Highlighting Engine
The client implements a zero-dependency lexical tokenizer (`highlightSyntax`) in `frontend/app.js`:
- **Supported Languages**: Python, JavaScript, TypeScript, Java, SQL, JSON, Bash, PowerShell, HTML/XML, CSS, YAML, Markdown.
- **Token Classification**:
  - `.tok-keyword`: Language control structures (`def`, `class`, `function`, `SELECT`, `async`, etc.).
  - `.tok-string`: Quoted string literals (`"..."`, `'...'`, `` `...` ``).
  - `.tok-comment`: Inline and block comments (`#`, `//`, `/* */`, `--`).
  - `.tok-number`: Numeric literals and hexadecimals.
  - `.tok-boolean`: Boolean constants (`true`, `false`, `None`, `null`).
  - `.tok-function`: Invocation and definition signatures (`functionName(...)`).
  - `.tok-type`: Common data types (`int`, `str`, `List`, `Promise`, `boolean`).
  - `.tok-operator`: Comparison, arithmetic, and logical operators (`==`, `!=`, `&&`, `||`).
- **Resilience**: Unknown languages fallback cleanly to HTML-escaped monospace blocks without crashing.

### 4.2 Safe Markdown & XSS Protection
- **Pure String Escaping**: `escapeHtml` avoids DOM mutation pitfalls by performing exact entity replacement (`&amp;`, `&lt;`, `&gt;`, `&quot;`, `&#39;`).
- **Safe URL Sanitizer (`sanitizeUrl`)**: Validates hyperlinks against `/^(https?:\/\/|mailto:)/i`. Malformed links or dangerous protocols (`javascript:`, `vbscript:`, `data:`) are replaced with `#blocked-unsafe-url`.
- **Placeholder Non-Collision**: Code blocks use `@@AEGIS-CODE-BLOCK-${idx}@@` placeholders to prevent collisions with Markdown italic/bold regex tokens (`__` or `*`).
- **Unclosed Code Fence Recovery**: Dangling code blocks (e.g. from interrupted responses) are automatically closed to prevent UI corruption.

### 4.3 Client-Side Cancellation Engine (`AbortController`)
- When generation starts, `currentAbortController = new AbortController()`.
- The stop button (`#btnStop`) and `Escape` key invoke `abortGeneration()`.
- The in-flight HTTP request is aborted, network traffic halts immediately, and the client renders:
  ```
  ⏹️ Generation cancelled by user.
  ```
- Composer state, buttons, and conversation history are restored without duplicate records.

---

## 5. Security & Isolation Architecture

### 5.1 Workspace Sandboxing & Path Traversal Guard
- **Workspace Jail**: All file reads, writes, and listings are confined to `./workspace` (`app/security/workspace.py`).
- **Canonicalization**: Paths are resolved using `os.path.realpath`. Any path resolving outside the root is blocked with `PermissionError`.
- **Forbidden Targets**: Direct access to `.env`, `.git/`, `.ssh/`, and system root files is prohibited.
- **Conflict Prevention**: Prior to applying patches, Aegis computes file hashes to prevent overwriting uncommitted out-of-band edits.

### 5.2 Automated Pre-Modification Rollback Backups
- Before any file modification is committed, the current file contents are archived in `.aegis_backups/<timestamp>_<filename>`.
- If an applied patch introduces regressions, the user can restore previous revisions directly from the backup directory.

### 5.3 Human Approval Lifecycle
Consequential actions must transition through a strict approval state machine:
```
PROPOSED -> PENDING_APPROVAL -> [USER DECISION] -> APPROVED -> EXECUTING -> SUCCEEDED / FAILED
                                                -> REJECTED
```
- **Patches**: Displayed as color-coded unified diffs showing exact additions and deletions.
- **Commands**: Restricted strictly to allowlisted test runners (`pytest`, `python -m unittest`, `npm test`). Arbitrary shell execution (`rm`, `curl`, `bash`) is rejected by the validator.

### 5.4 Secret Shield & Audit Logging
- Every prompt, memory entry, and log line passes through regex-based secret filters redacting API keys, Bearer tokens, and private keys.
- All approval decisions and execution results are recorded in the immutable SQLite `audit_log` table.

---

## 6. Storage & Database Schema

Aegis AI uses embedded SQLite (`aegis.db`) with foreign keys enabled:

1. **`conversations`**:
   - `id` (TEXT PRIMARY KEY), `title` (TEXT), `created_at` (DATETIME), `updated_at` (DATETIME).
2. **`messages`**:
   - `id` (TEXT PRIMARY KEY), `conversation_id` (TEXT FK), `role` (TEXT), `content` (TEXT), `created_at` (DATETIME).
3. **`memories`**:
   - `id` (TEXT PRIMARY KEY), `content` (TEXT), `category` (TEXT), `tags` (TEXT), `created_at` (DATETIME).
4. **`approvals`**:
   - `id` (TEXT PRIMARY KEY), `action_type` (TEXT: `patch`, `command`, `task`), `target` (TEXT), `details` (TEXT), `diff` (TEXT), `risk_level` (TEXT), `status` (TEXT), `created_at` (DATETIME), `updated_at` (DATETIME).
5. **`audit_log`**:
   - `id` (INTEGER PRIMARY KEY AUTOINCREMENT), `event_type` (TEXT), `details` (TEXT), `timestamp` (DATETIME).
6. **`projects` & `tasks`**:
   - Backlog organization linking goals to individual task milestones.

---

## 7. Important Modules & Responsibilities

| Path | Primary Responsibility |
|---|---|
| [`main.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/main.py) | Application entrypoint, FastAPI instance, static file mounts, database lifecycle hooks. |
| [`app/config.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/app/config.py) | Configuration settings, environment variables, thread-safe provider state management. |
| [`app/api/chat.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/app/api/chat.py) | Chat endpoint (`POST /api/chat`), conversation session management, rename endpoint. |
| [`app/api/provider.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/app/api/provider.py) | Provider switching (`POST /api/provider`) and connectivity inspection (`GET /api/provider`). |
| [`app/api/health.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/app/api/health.py) | Readiness probe (`GET /api/health`), database connection check, sanitized provider tags. |
| [`app/api/approvals.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/app/api/approvals.py) | Human approval decision endpoints (`POST /api/approvals/{id}/approve`, reject). |
| [`app/api/workspace.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/app/api/workspace.py) | Workspace exploration, file content reading, manual diff generation. |
| [`app/api/memory.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/app/api/memory.py) | Memory CRUD endpoints, keyword queries, secret protection. |
| [`app/api/projects.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/app/api/projects.py) | Project and milestone task backlog endpoints. |
| [`app/services/agent_service.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/app/services/agent_service.py) | Prompt enrichment, memory retrieval, approval parsing, provider snapshotting. |
| [`app/services/llm_service.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/app/services/llm_service.py) | Dual-provider dispatcher: Ollama HTTP integration and Cloud OpenAI integration. |
| [`app/services/memory_service.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/app/services/memory_service.py) | SQLite memory repository, keyword index matching, token scrubbing. |
| [`app/security/workspace.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/app/security/workspace.py) | Path traversal verification, safe file I/O, timestamped backup engine. |
| [`app/security/approvals.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/app/security/approvals.py) | Command allowlist verification, approval state transitions, patch execution. |
| [`frontend/index.html`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/frontend/index.html) | ChatGPT-inspired DOM layout, collapsible sidebar, stop button, toast container. |
| [`frontend/app.js`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/frontend/app.js) | Syntax highlighting, safe Markdown engine, AbortController, clipboard actions. |
| [`frontend/styles.css`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/frontend/styles.css) | Obsidian dark theme, syntax highlighting tokens, toast styling, responsive layout. |
| [`skills/`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/skills/) | Reusable developer skill definitions (Planner, Explainer, Debugger, Test Writer). |
