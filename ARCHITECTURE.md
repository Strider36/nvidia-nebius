# Aegis AI — System Architecture Document

**Version:** 0.7.0  
**Status:** Approved & Current Baseline  
**Date:** 2026-10-30  

---

## 1. Executive Summary

Aegis AI is a privacy-first, developer-centric personal AI operator and autonomous coding assistant built around three foundational pillars:
1. **Dual-Provider Inference with Strict Isolation & Native Streaming**: Seamlessly switch between zero-data-leakage local inference via **Ollama** (`http://127.0.0.1:11434`) running **NVIDIA Nemotron 3.5 Bolt E4B** and high-throughput cloud inference via **Nebius Token Factory** or **OpenRouter** (`https://openrouter.ai/api/v1`). Supports native real-time SSE token streaming (`POST /api/chat/stream`) and strict isolation with zero silent fallbacks.
2. **Human-in-the-Loop Security & Workspace Sandboxing**: All file modifications and shell executions are sandboxed inside `./workspace` (or configured `AEGIS_WORKSPACE`). Automatic timestamped backups are generated in `.aegis_backups/`, and every patch or allowlisted test runner command requires explicit human review and approval.
3. **Unified Premium Design System Across Every Application View**: Distinctive developer-first design identity built on Obsidian canvas (`#0B0C0F`), Graphite sidebar (`#101116`), elevated surfaces (`#15171D`, `#1B1D25`), Platinum text (`#E6E4EC`), and Electric Violet accents (`#A78BFA`). Features crisp hairline borders (`#292B32`), mathematical typography and systematic spacing tokens, a shared component foundation (`.btn-*`, `.status-pill`, `.data-table`, `.empty-state`, `.panel-card`), a standardized modal subsystem, bespoke geometric SVG icons (zero emoji glyphs), a zero-dependency multi-language syntax highlighter, and a cohesive physics-based motion system (`--ease-out`).

---

## 2. High-Level System Architecture Diagram

```
+-------------------------------------------------------------------------------------------------------+
|                                              BROWSER CLIENT                                           |
|                                                                                                       |
|  +---------------------------+  +-------------------------------+  +-------------------------------+  |
|  | Graphite Collapsible Bar  |  | Centered Reading Stream       |  | Streaming & Motion System     |  |
|  | - Realtime Search & Date  |  | - 48rem Focused Column        |  | - Native SSE Token Decoding   |  |
|  | - Grouped History Items   |  | - Obsidian/Graphite Surfaces  |  | - Auto-Scroll Lock (<=160px)  |  |
|  | - Mobile Off-Canvas Drawer|  | - Bespoke Geometric SVG Icons |  | - Blinking Cursor & Markdown  |  |
|  | - Settings Modal Trigger  |  | - Flat Surface Hierarchy      |  | - AbortController (#btnStop)  |  |
|  +---------------------------+  +-------------------------------+  +-------------------------------+  |
|                                                                                                       |
|  +-------------------------------------------------------------------------------------------------+  |
|  | Standardized Modal Dialog Subsystem (.modal-content, .modal-title-group, .btn-close)             |  |
|  | - Skills Catalog: Dynamic grid, .tool-tag badges, .status-pill indicators                      |  |
|  | - Memory Vault: Flat elevated add form, category filter pills, .memory-card list                |  |
|  | - Approvals Center: Unified diff viewer, risk badges, approve/reject workflow                   |  |
|  | - Workspace Explorer: Sandboxed directory navigation, SVG file tree, code preview              |  |
|  | - Security Audit: High-density data table, sticky graphite headers, monospace timestamps        |  |
|  | - Settings & Diagnostics: Live provider verification, network boundary audits, health check    |  |
|  +-------------------------------------------------------------------------------------------------+  |
+-------------------------------------------------------------------------------------------------------+
                                                   |
                                                   | HTTP REST / SSE (text/event-stream)
                                                   v
+-------------------------------------------------------------------------------------------------------+
|                                           FASTAPI BACKEND SERVICE                                     |
|                                                                                                       |
|  API Routers:                                                                                         |
|  - /api/chat/stream -> Real-time chunked SSE token generator with client disconnect handling           |
|  - /api/chat        -> Non-streaming chat orchestrator, history, memory injection, approval parsing  |
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

## 3. Unified Design System & Styling Architecture (v0.7.0)

### 3.1 Centralized Design Tokens
Centralized in `frontend/styles.css` without ad-hoc rules:
```css
:root {
  /* Surfaces */
  --bg-primary: #0B0C0F;       /* Obsidian main canvas */
  --bg-sidebar: #101116;       /* Graphite sidebar */
  --bg-secondary: #15171D;     /* Composer, cards, nav items */
  --bg-elevated: #1B1D25;      /* Modals, popovers, active pills */
  --bg-hover: #222530;         /* Interactive hover */
  --bg-active: #2A2E3B;        /* Pressed / selected state */

  /* Hairline Crisp Borders */
  --border-subtle: #292B32;    /* Hairline boundary */
  --border-active: #3D414D;    /* Interactive focus border */
  --border-accent: #A78BFA;    /* Electric violet focus ring */

  /* Platinum Typography */
  --text-primary: #E6E4EC;     /* High contrast body (WCAG AAA) */
  --text-secondary: #A2A2AF;   /* Secondary slate (WCAG AA) */
  --text-muted: #777986;       /* Muted labels (WCAG AA) */

  /* Electric Violet Accent System */
  --accent-primary: #A78BFA;   /* Electric violet base */
  --accent-hover: #B9A5FF;     /* Violet hover highlight */
  --accent-subtle: rgba(167, 139, 250, 0.12);
  --accent-glow: rgba(167, 139, 250, 0.28);
  --accent-gradient: linear-gradient(135deg, #A78BFA, #7C3AED);

  /* Semantic State Tokens */
  --color-success: #62C9A0;    /* Sage mint */
  --color-warning: #E7B96A;    /* Warm amber */
  --color-error: #F07878;      /* Coral rose */

  /* Mathematical Typography Scale */
  --font-size-2xs: 0.68rem;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.82rem;
  --font-size-base: 0.88rem;
  --font-size-md: 0.95rem;
  --font-size-lg: 1.08rem;
  --font-size-xl: 1.30rem;
  --font-size-2xl: 1.60rem;

  /* Systematic Spacing Scale */
  --space-3xs: 2px;
  --space-2xs: 4px;
  --space-xs: 8px;
  --space-sm: 12px;
  --space-md: 16px;
  --space-lg: 20px;
  --space-xl: 24px;
  --space-2xl: 32px;
}
```

### 3.2 Shared Component Foundation
Every page in Aegis AI reuses a core set of standard components:
1. **Buttons (`.btn-*`)**: `.btn-primary` (Electric Violet), `.btn-secondary` (Graphite surface), `.btn-outline` (Hairline border), `.btn-ghost` (Transparent interactive), `.btn-danger` (Coral rose state), and `.btn-close` (28x28px geometric SVG icon button).
2. **Status Pills (`.status-pill`)**: Semantic badge with a glowing status dot (`.status-pill.success`, `.status-pill.warning`, `.status-pill.error`, `.status-pill.active`).
3. **Data Tables (`.data-table`, `.audit-table`)**: Sticky graphite headers (`#101116`), subtle hairline borders (`#292B32`), high-density rows, and monospace timestamps (`.mono-time`).
4. **Empty States (`.empty-state`)**: Centered geometric SVG icons, clear primary headings, and secondary action hints.
5. **Panel Cards (`.panel-card`, `.list-item-card`)**: Controlled single-layer elevation with subtle border transition on hover.
6. **Form Controls (`.form-control`)**: Graphite background, hairline border `#292B32`, Electric Violet focus ring, clear label hierarchy.
7. **Tabs (`.tab-pill-bar`, `.btn-tab`)**: Segmented pill bars for memory and workspace filtering.

### 3.3 Modal Dialog Subsystem
All modal dialogs (Skills, Memory, Approvals, Workspace, Audit, Settings) share a unified layout:
- **Header**: `.modal-title-group` with bespoke geometric SVG icon, crisp `<h3>` title, and `.modal-subtitle` explanation.
- **Close Button**: Standard `.btn-close` housing an accessible SVG icon (`aria-label="Close modal"`).
- **Body & Footer**: Standardized padding (`--space-lg`), secondary surface background, and clear separation lines.
- **Zero Card-in-Card Nesting**: Elimination of redundant nested `.card` blocks inside dialogs, maintaining visual clarity.

### 3.4 Motion System Architecture
- **Physics Tokens**:
  - `--ease-out`: `cubic-bezier(0.16, 1, 0.3, 1)`
  - `--ease-in-out`: `cubic-bezier(0.4, 0, 0.2, 1)`
  - `--duration-fast`: `150ms` (hover, active press, focus rings)
  - `--duration-normal`: `220ms` (toasts, cards, panels)
  - `--duration-slow`: `360ms` (welcome hero, modal entrances)
- **Keyframe Sequences**:
  - `@keyframes heroEntrance`: Smooth fade and rise (opacity from 0 to 1, translateY from 10px to 0).
  - `@keyframes chipEntrance`: Staggered appearance of prompt suggestion chips (`60ms`, `110ms`, `160ms`, `210ms`).
  - `@keyframes modalPop`: Elevated surfaces entrance (scale from 0.98 to 1.0, opacity from 0 to 1).
  - `@keyframes dotPulse`: Restrained thinking pulse wave.
- **Accessibility**: `@media (prefers-reduced-motion: reduce)` zeroes out animation durations, providing instant layout presentation for sensitive users.

### 3.5 Pure Geometric SVG Iconography
Platform-dependent emoji glyphs (`📋`, `🔍`, `🐞`, `🧪`, `🧠`, `⚙️`) have been entirely eliminated. The interface utilizes uniform 1.75px stroke geometric inline SVGs styled with CSS tokens, guaranteeing identical visual rendering across Windows, macOS, and Linux.

---

## 4. End-to-End Request Lifecycle

Tracing a complete request from the user's keystroke through to the final rendered UI:

1. **User Action**: The user enters a prompt into `#messageInput` and presses `Enter` (or clicks `#btnSend`).
2. **Client State Preparation**:
   - `frontend/app.js` checks if a request is already active; if so, returns early.
   - An `AbortController` instance is instantiated and stored in `currentAbortController`.
   - The UI updates: `#btnSend` hides, `#btnStop` reveals with an active pulse.
   - A user message node is rendered into the chat container.
3. **HTTP Dispatch**:
   - Client sends `POST /api/chat` with `{ message, conversation_id, project_id, skill_id, provider }` passing `{ signal: currentAbortController.signal }`.
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
   - Backend returns `{ assistant_message, conversation_id, pending_approvals: [...] }`.
   - `frontend/app.js` runs `renderSafeMarkdown(assistant_message)`:
     - Fenced code blocks are isolated into `@@AEGIS-CODE-BLOCK-${idx}@@` placeholders.
     - Tables are converted into responsive HTML with `.msg-table-wrapper` horizontal scrollers.
     - Lists, headings, quotes, and inline styles are formatted.
     - Code placeholders are restored with syntax highlighting via `highlightSyntax(code, lang)`.
     - Code header chrome with language badge and copy button is injected.
   - Approval cards are rendered with interactive **Approve** and **Reject** buttons and unified diff viewers.
   - `#btnStop` hides, `#btnSend` returns.

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
| [`frontend/index.html`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/frontend/index.html) | Geometric SVG icons, collapsible sidebar, stop button, toast container. |
| [`frontend/app.js`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/frontend/app.js) | Syntax highlighting, safe Markdown engine, AbortController, clipboard actions. |
| [`frontend/styles.css`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/frontend/styles.css) | Obsidian & Electric Violet theme, motion system tokens, responsive layout. |
| [`skills/`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/skills/) | Reusable developer skill definitions (Planner, Explainer, Debugger, Test Writer). |
