# Aegis AI — Task Tracker & Backlog

**Version Baseline:** 0.4.0  
**Last Updated:** 2026-10-29  
**Status Key:**  
- `[DONE]` Completed, verified with automated tests, and documented.
- `[IN_PROGRESS]` Currently active development.
- `[PLANNED]` Backlog item scheduled for upcoming release.

---

## 1. Milestone 4: Premium Response Experience & Complete Documentation (v0.4.0)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-401** | Audit response rendering lifecycle from composer to DOM | High | `[DONE]` | None | Traced request flow, identified CRLF parsing traps, documented findings in `audit_response_rendering.md`. |
| **TASK-402** | Zero-dependency multi-language syntax highlighter | High | `[DONE]` | TASK-401 | Native tokenizer supporting 12+ languages (Python, JS, TS, Java, SQL, JSON, Bash, PS, HTML, CSS, YAML, MD) with dark theme tokens. |
| **TASK-403** | Resilient Markdown engine & GFM tables | High | `[DONE]` | TASK-401 | Render headings, blockquotes, inline formatting, table wrappers with overflow scroll, and arbitrarily nested lists. |
| **TASK-404** | Safe URL sanitization & XSS guard | Critical | `[DONE]` | TASK-403 | Block `javascript:`, `vbscript:`, and `data:` URIs; allow only `http(s)://` and `mailto:`. |
| **TASK-405** | Unclosed code block recovery | Medium | `[DONE]` | TASK-402 | Automatically close dangling code fences during incomplete responses without breaking layout. |
| **TASK-406** | Copy response action & toast notifications | Medium | `[DONE]` | TASK-403 | One-click button to copy assistant response to clipboard with animated toast notification and `execCommand` fallback. |
| **TASK-407** | Copy code block action | Medium | `[DONE]` | TASK-402 | Individual copy button in code block header with visual checkmark confirmation and clipboard error handling. |
| **TASK-408** | Client-side request cancellation (`AbortController`) | High | `[DONE]` | None | `#btnStop` button and `Escape` key trigger abort signal, halt HTTP request, and restore composer state cleanly. |
| **TASK-409** | Node.js frontend markdown test suite | High | `[DONE]` | TASK-402, TASK-404 | 11 automated test cases verifying syntax tokens, sanitization, table wrappers, nested lists, and unclosed blocks. |
| **TASK-410** | Python frontend integration tests | High | `[DONE]` | TASK-406, TASK-408 | Added assertions for `#btnStop`, `#toastContainer`, `highlightSyntax`, and `.tok-keyword` in `tests/test_frontend.py`. |
| **TASK-411** | Documentation: PRD.md | High | `[DONE]` | All v0.4.0 | Detailed product requirements covering target users, functional/nonfunctional reqs, provider behaviors, acceptance criteria. |
| **TASK-412** | Documentation: IMPLEMENTATION_PLAN.md | High | `[DONE]` | All v0.4.0 | Milestones 1–4 completed breakdown, Milestone 5 roadmap, dependencies, risks, mitigations, and quality gates. |
| **TASK-413** | Documentation: TASKS.md | High | `[DONE]` | All v0.4.0 | Comprehensive task tracker with task IDs, priorities, statuses, dependencies, and acceptance criteria. |
| **TASK-414** | Documentation: ARCHITECTURE.md reconciliation | High | `[DONE]` | All v0.4.0 | Updated request flow diagram, syntax highlighting engine, abort pipeline, memory model, and module inventory. |
| **TASK-415** | Documentation: README.md & TESTING.md updates | High | `[DONE]` | All v0.4.0 | Document setup, Windows 11 prerequisites, test commands, latest results, and environment configuration. |
| **TASK-416** | CHANGELOG.md & version bump to 0.4.0 | Medium | `[DONE]` | All v0.4.0 | Update version in `app/__init__.py`, `pyproject.toml`, and record entry in `CHANGELOG.md`. |

---

## 2. Milestone 3: ChatGPT-Inspired Interface Redesign (v0.3.0)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-301** | Obsidian dark color palette & design tokens | High | `[DONE]` | None | Implement `#0d0d0d`, `#171717`, `#212121`, and cyan `#06b6d4` design variables in `frontend/styles.css`. |
| **TASK-302** | Collapsible history sidebar with search | High | `[DONE]` | TASK-301 | Client-side search input `#conversationSearchInput` filtering sessions in real-time with clear button. |
| **TASK-303** | Chronological conversation date grouping | Medium | `[DONE]` | TASK-302 | Group sessions by `Today`, `Yesterday`, `Previous 7 Days`, and `Older`. |
| **TASK-304** | Conversation renaming backend & UI | Medium | `[DONE]` | TASK-302 | Add `PATCH /api/conversations/{id}` endpoint and click-to-rename UI controls. |
| **TASK-305** | ChatGPT-style welcome hero with suggestion chips | Medium | `[DONE]` | TASK-301 | Welcome headline and 4 compact suggestion chips (`Plan a Project`, `Explain Code`, `Debug an Issue`, `Generate Tests`). |
| **TASK-306** | Centered reading column & auto-resizing composer | High | `[DONE]` | TASK-301 | Centered `max-width: 48rem` column with textarea expanding from 36px to 180px with Enter-to-send. |
| **TASK-307** | Responsive mobile drawer & touch overlay | High | `[DONE]` | TASK-302 | Off-canvas sidebar drawer for viewport `<= 768px` with backdrop dismiss and safe-area insets. |

---

## 3. Milestone 2: Dual-Provider Inference & Anti-Fallback Invariant (v0.2.0)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-201** | Local Ollama HTTP client integration | Critical | `[DONE]` | None | Async HTTP requests to `http://127.0.0.1:11434/api/chat` with NVIDIA Nemotron 3.5 Bolt E4B support. |
| **TASK-202** | Cloud provider integration (Nebius/OpenRouter) | Critical | `[DONE]` | None | OpenAI SDK compatible client using `NEBIUS_BASE_URL` and `NEBIUS_MODEL_ID`. |
| **TASK-203** | Thread-safe runtime provider switching | High | `[DONE]` | TASK-201, 202 | Thread-safe `_provider_lock` and `POST /api/provider` allowing dynamic switching without restart. |
| **TASK-204** | Non-blocking provider reachability probe | Medium | `[DONE]` | TASK-201 | Query `/api/tags` with strict 2.0s timeout to prevent server boot hang when Ollama is offline. |
| **TASK-205** | Per-request provider snapshotting in AgentService | Critical | `[DONE]` | TASK-203 | Snapshot provider choice per request to eliminate race conditions in concurrent multi-turn chats. |
| **TASK-206** | Anti-fallback invariant verification | Critical | `[DONE]` | TASK-205 | 12 tests in `tests/test_provider.py` confirming zero cloud fallback on Ollama failure or timeout. |
| **TASK-207** | Provider error sanitization | Medium | `[DONE]` | TASK-201 | Specific error guidance for HTTP 404 (model missing), connection refused, and timeout. |

---

## 4. Milestone 1: Core Foundation & Safe Sandbox (v0.1.0)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-101** | Restricted workspace sandbox (`./workspace`) | Critical | `[DONE]` | None | Canonical path resolution, strict isolation inside `./workspace`, blocking `../` traversal. |
| **TASK-102** | Automatic pre-modification backups | High | `[DONE]` | TASK-101 | Store timestamped rollback files in `.aegis_backups/` before any patch is written. |
| **TASK-103** | Human-in-the-loop patch approval lifecycle | Critical | `[DONE]` | TASK-101 | Consequential actions require explicit approval; zero autonomous self-approval. |
| **TASK-104** | Command allowlist verification | Critical | `[DONE]` | TASK-103 | Only allowlisted test commands (`pytest`, `unittest`, `npm test`) can be executed with timeouts. |
| **TASK-105** | Persistent SQLite memory & keyword indexing | High | `[DONE]` | None | Persistent storage of preferences, facts, and context; keyword matching; sensitive secret filtering. |
| **TASK-106** | Developer skills framework | Medium | `[DONE]` | None | Modular system prompts and tool bindings for Project Planner, Code Explainer, Debugger, Test Writer. |
| **TASK-107** | Security audit trail persistence | High | `[DONE]` | TASK-103 | Immutable event logging to SQLite with automatic secret and token redaction. |

---

## 5. Milestone 5: Native Token Streaming & Advanced Tooling (v0.5.0 — Planned)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-501** | Backend SSE streaming endpoint | High | `[PLANNED]` | None | `POST /api/chat/stream` delivering `text/event-stream` tokens from active provider. |
| **TASK-502** | Ollama async token generator | High | `[PLANNED]` | TASK-501 | Consume Ollama HTTP streaming payload chunk-by-chunk without blocking the event loop. |
| **TASK-503** | Cloud OpenAI async token generator | High | `[PLANNED]` | TASK-501 | Stream chunks from Nebius/OpenRouter using `stream=True`. |
| **TASK-504** | Client incremental token renderer | High | `[PLANNED]` | TASK-501 | Append incoming tokens smoothly to active assistant turn; debounce syntax highlighting. |
| **TASK-505** | Smart viewport auto-scroll lock | Medium | `[PLANNED]` | TASK-504 | Automatically scroll if user is within 60px of bottom; freeze position if user scrolls up. |
| **TASK-506** | Server-side stream cancellation handler | High | `[PLANNED]` | TASK-501 | Cancel backend inference loop immediately when client disconnects or aborts. |
