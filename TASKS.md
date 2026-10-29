# Aegis AI — Task Tracker & Backlog

**Version Baseline:** 0.8.1  
**Last Updated:** 2026-10-30  
**Status Key:**  
- `[DONE]` Completed, verified with automated tests, and documented.
- `[IN_PROGRESS]` Currently active development.
- `[PLANNED]` Backlog item scheduled for upcoming release.

---

## 1. Milestone 9: Full-System Optimization, Reliability & Verification (v0.8.1 — Completed)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-901** | Full repository audit & discrepancy identification | Critical | `[DONE]` | None | Completed comprehensive audit of backend routes, Hermes service, subprocess I/O, SQLite layers, and frontend state. |
| **TASK-902** | FastAPI version metadata synchronization | High | `[DONE]` | TASK-901 | Synchronized `FastAPI(..., version=__version__)` in `main.py` to resolve version drift against `app/__init__.py`. |
| **TASK-903** | Subprocess Windows character encoding resilience | Critical | `[DONE]` | TASK-901 | Hardened `hermes_service.py` and `workspace_service.py` with `encoding="utf-8", errors="replace"` to prevent Windows cp1252 crash on LLM emojis and unicode output. |
| **TASK-904** | Subprocess timeout & process termination hardening | Critical | `[DONE]` | TASK-901 | Hardened Hermes process iteration, stream cleanup on disconnect (`GeneratorExit`), and child process termination. |
| **TASK-905** | Workspace sandbox & backup verification | Critical | `[DONE]` | TASK-901 | Verified path traversal defenses, symlink resolution, `.aegis_backups` automated pre-modification snapshots, and allowlisted test execution inside sandboxed `./workspace`. |
| **TASK-906** | End-to-end integration & lifecycle test suite | Critical | `[DONE]` | TASK-901 | Added `tests/test_e2e_live.py` (4 tests) covering metadata sync, secret-free provider inspection, and complete multi-step human approval lifecycle. |
| **TASK-907** | Total automated regression test run | Critical | `[DONE]` | All | Executed 80 automated tests (69 Python + 11 Node) with 100% pass rate. |

---

## 2. Milestone 8: Hermes Agent Backend Integration (v0.8.0 — Completed)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-801** | Hermes host environment audit & verification | Critical | `[DONE]` | None | Detected `hermes.exe` at `C:\Users\jayan\AppData\Local\hermes\bin\hermes.exe` (v0.22.5); verified Ollama Nemotron CLI invocation. |
| **TASK-802** | HermesService subprocess adapter | High | `[DONE]` | TASK-801 | Built `app/services/hermes_service.py` with query file composition, timeout controls, and process cleanup. |
| **TASK-803** | JSONL streaming protocol & SSE bridge | High | `[DONE]` | TASK-802 | Streamed tokens line-by-line (`{"type": "text", "text": "..."}`) into Aegis `/api/chat/stream` SSE channel. |
| **TASK-804** | Subprocess workspace sandboxing & tool suppression | Critical | `[DONE]` | TASK-802 | Enforced `--in <workspace_path>` and suppressed unsupervised internal tools with `--toolsets ""`. |
| **TASK-805** | Human approval extraction for Hermes proposals | Critical | `[DONE]` | TASK-802 | Intercepted `<<<PROPOSE_PATCH>>>`, `<<<PROPOSE_COMMAND>>>` tags from Hermes output into SQLite `pending_approvals`. |
| **TASK-806** | Anti-fallback invariant verification | Critical | `[DONE]` | TASK-802 | Confirmed local Ollama failures with Hermes backend never silently fail over to cloud. |
| **TASK-807** | Frontend Agent Mode switcher & diagnostics card | High | `[DONE]` | TASK-802 | Added topbar `#agentModeSwitcher` toggle and `#settingsHermesCard` in Settings modal. |
| **TASK-808** | Automated test suite & end-to-end live task test | Critical | `[DONE]` | All v0.8.0 | Added `tests/test_hermes.py` (8 tests) and verified live end-to-end task (76 automated tests passing). |

---

## 2. Milestone 7: Unified Premium Design System Across Application (v0.7.0 — Completed)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-701** | Cross-application design audit & gap mapping | High | `[DONE]` | None | Documented fragmented styles, card-in-card nesting, raw `&times;` glyphs in `unified_design_audit.md`. |
| **TASK-702** | Centralized typography & systematic spacing scale | High | `[DONE]` | TASK-701 | Implemented `--font-size-2xs` (0.68rem) through `--font-size-2xl` (1.60rem) and `--space-3xs` to `--space-2xl` in `styles.css`. |
| **TASK-703** | Standardized shared component foundation | High | `[DONE]` | TASK-702 | Built reusable `.btn-*`, `.status-pill` with glow, `.data-table`, `.audit-table`, `.empty-state`, `.panel-card`. |
| **TASK-704** | Standardize modal dialog subsystem across all 6 views | High | `[DONE]` | TASK-703 | Uniform `.modal-title-group`, SVG title icons, subtitle descriptions, and `.btn-close` geometric SVG buttons. |
| **TASK-705** | Eliminate card-in-card nesting & de-clutter forms | Medium | `[DONE]` | TASK-703 | Flattened Add Memory form into elevated secondary surface with crisp `#292B32` hairline boundary. |
| **TASK-706** | Dedicated Settings & Provider Diagnostics modal (`#modalSettings`) | High | `[DONE]` | TASK-704 | Rendered live provider verification, loopback privacy boundary, database sandbox, and interactive diagnostics trigger. |
| **TASK-707** | Modernize dynamic table & card renderers | Medium | `[DONE]` | TASK-703 | Updated `renderModalProjects`, `loadTasksForProject`, `loadMemories`, `loadSkillsCatalog`, `loadWorkspaceBrowser`, `loadAuditTrail`, `loadModalApprovals`. |
| **TASK-708** | Unified design system & settings regression test suite | High | `[DONE]` | All v0.7.0 | Added `test_frontend_unified_design_system_and_settings()` in `tests/test_frontend.py` (67 tests passing). |

---

## 3. Milestone 6: Native Token Streaming & Advanced Tooling (v0.6.0 — Completed)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-601** | Backend SSE streaming endpoint | High | `[DONE]` | None | `POST /api/chat/stream` delivering `text/event-stream` tokens from active provider with anti-buffering headers. |
| **TASK-602** | Ollama native token generator | High | `[DONE]` | TASK-601 | Consume Ollama HTTP streaming payload chunk-by-chunk via `stream: true` in `LLMService._generate_stream_ollama`. |
| **TASK-603** | Cloud OpenAI native token generator | High | `[DONE]` | TASK-601 | Stream chunks from Nebius/OpenRouter using `stream=True` in `LLMService._generate_stream_cloud`. |
| **TASK-604** | Client incremental token renderer | High | `[DONE]` | TASK-601 | Append incoming tokens smoothly to active assistant turn with authentic blinking cursor (`.streaming-cursor`). |
| **TASK-605** | Smart viewport auto-scroll lock | Medium | `[DONE]` | TASK-604 | Automatically scroll if user is within 160px of bottom; freeze position if user scrolls up. |
| **TASK-606** | Server-side stream cancellation handler | High | `[DONE]` | TASK-601 | Handle `GeneratorExit` on client abort, persist partial response to SQLite with `*(Generation stopped by user)*`. |
| **TASK-607** | Streaming regression test suite | High | `[DONE]` | All v0.6.0 | Added 9 new tests across `test_chat.py`, `test_llm.py`, `test_provider.py`, `test_frontend.py` (66 tests total). |

---

## 4. Milestone 5: Obsidian/Violet Theme, Motion System & SVGs (v0.5.0 — Completed)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-501** | Visual audit of frontend layouts, colors, and motion gaps | High | `[DONE]` | None | Identified generic card clutter, emoji usage, contrast ratios; documented in `visual_audit_redesign.md`. |
| **TASK-502** | Implement Obsidian, Graphite, Platinum & Electric Violet design system | High | `[DONE]` | TASK-501 | Centralized tokens in `styles.css`: `#0B0C0F`, `#101116`, `#15171D`, `#1B1D25`, `#E6E4EC`, `#A78BFA`. |
| **TASK-503** | Pure geometric SVG iconography architecture | High | `[DONE]` | TASK-502 | Replaced platform emojis with uniform 1.75px geometric SVGs across suggestion chips, memory pills, and approval cards. |
| **TASK-504** | Build cohesive physics-based motion system | High | `[DONE]` | TASK-502 | Added `--ease-out`, `--duration-fast/normal/slow`, `@keyframes heroEntrance`, staggered `@keyframes chipEntrance`. |
| **TASK-505** | Micro-interactions, button presses & focus rings | Medium | `[DONE]` | TASK-504 | Button press scaling (`scale(0.98)`), smooth focus rings with Violet glow (`rgba(167, 139, 250, 0.28)`). |
| **TASK-506** | Harmonize syntax highlighting token palette | Medium | `[DONE]` | TASK-502 | Updated `.tok-keyword`, `.tok-string`, `.tok-comment`, `.tok-function` to match Platinum & Violet palette. |
| **TASK-507** | Design system & motion regression test suite | High | `[DONE]` | TASK-502, TASK-504 | Added `test_frontend_obsidian_violet_design_system_and_motion` in `tests/test_frontend.py` (57 tests total). |
| **TASK-508** | Complete documentation suite & version bump to v0.5.0 | High | `[DONE]` | All v0.5.0 | Updated `PRD.md`, `README.md`, `ARCHITECTURE.md`, `IMPLEMENTATION_PLAN.md`, `TASKS.md`, `TESTING.md`, `CHANGELOG.md`. |

---

## 5. Milestone 4: Premium Response Experience & Complete Documentation (v0.4.0 — Completed)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-401** | Audit response rendering lifecycle from composer to DOM | High | `[DONE]` | None | Traced request flow, identified CRLF parsing traps, documented findings in `audit_response_rendering.md`. |
| **TASK-402** | Zero-dependency multi-language syntax highlighter | High | `[DONE]` | TASK-401 | Native tokenizer supporting 12+ languages with dark theme tokens. |
| **TASK-403** | Resilient Markdown engine & GFM tables | High | `[DONE]` | TASK-401 | Render headings, blockquotes, inline formatting, table wrappers with overflow scroll, and arbitrarily nested lists. |
| **TASK-404** | Safe URL sanitization & XSS guard | Critical | `[DONE]` | TASK-403 | Block `javascript:`, `vbscript:`, and `data:` URIs; allow only `http(s)://` and `mailto:`. |
| **TASK-405** | Unclosed code block recovery | Medium | `[DONE]` | TASK-402 | Automatically close dangling code fences during incomplete responses without breaking layout. |
| **TASK-406** | Copy response action & toast notifications | Medium | `[DONE]` | TASK-403 | One-click button to copy assistant response to clipboard with animated toast notification and `execCommand` fallback. |
| **TASK-407** | Copy code block action | Medium | `[DONE]` | TASK-402 | Individual copy button in code block header with visual checkmark confirmation and clipboard error handling. |
| **TASK-408** | Client-side request cancellation (`AbortController`) | High | `[DONE]` | None | `#btnStop` button and `Escape` key trigger abort signal, halt HTTP request, and restore composer state cleanly. |
| **TASK-409** | Node.js frontend markdown test suite | High | `[DONE]` | TASK-402, TASK-404 | 11 automated test cases verifying syntax tokens, sanitization, table wrappers, nested lists, and unclosed blocks. |

---

## 6. Milestone 3: Interface Layout & Conversation Architecture (v0.3.0 — Completed)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-301** | Obsidian dark color palette & design tokens | High | `[DONE]` | None | Base design variables in `frontend/styles.css`. |
| **TASK-302** | Collapsible history sidebar with search | High | `[DONE]` | TASK-301 | Client-side search input `#conversationSearchInput` filtering sessions in real-time with clear button. |
| **TASK-303** | Chronological conversation date grouping | Medium | `[DONE]` | TASK-302 | Group sessions by `Today`, `Yesterday`, `Previous 7 Days`, and `Older`. |
| **TASK-304** | Conversation renaming backend & UI | Medium | `[DONE]` | TASK-302 | Add `PATCH /api/conversations/{id}` endpoint and click-to-rename UI controls. |
| **TASK-305** | Welcome hero with compact suggestion chips | Medium | `[DONE]` | TASK-301 | Welcome headline and 4 compact suggestion chips. |
| **TASK-306** | Centered reading column & auto-resizing composer | High | `[DONE]` | TASK-301 | Centered `max-width: 48rem` column with textarea expanding from 36px to 180px with Enter-to-send. |
| **TASK-307** | Responsive mobile drawer & touch overlay | High | `[DONE]` | TASK-302 | Off-canvas sidebar drawer for viewport `<= 768px` with backdrop dismiss and safe-area insets. |

---

## 7. Milestone 2: Dual-Provider Inference & Anti-Fallback Invariant (v0.2.0 — Completed)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-201** | Local Ollama HTTP client integration | Critical | `[DONE]` | None | Async HTTP requests to `http://127.0.0.1:11434/api/chat` with NVIDIA Nemotron 3.5 Bolt E4B support. |
| **TASK-202** | Cloud provider integration (Nebius/OpenRouter) | Critical | `[DONE]` | None | OpenAI SDK compatible client using `NEBIUS_BASE_URL` and `NEBIUS_MODEL_ID`. |
| **TASK-203** | Thread-safe runtime provider switching | High | `[DONE]` | TASK-201, 202 | Thread-safe `_provider_lock` and `POST /api/provider` allowing dynamic switching without restart. |
| **TASK-204** | Non-blocking provider reachability probe | Medium | `[DONE]` | TASK-201 | Query `/api/tags` with strict 2.0s timeout to prevent server boot hang when Ollama is offline. |
| **TASK-205** | Per-request provider snapshotting in AgentService | Critical | `[DONE]` | TASK-203 | Snapshot provider choice per request to eliminate race conditions in concurrent multi-turn chats. |
| **TASK-206** | Anti-fallback invariant verification | Critical | `[DONE]` | TASK-205 | 12 tests in `tests/test_provider.py` confirming zero cloud fallback on Ollama failure or timeout. |

---

## 8. Milestone 1: Core Foundation & Safe Sandbox (v0.1.0 — Completed)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-101** | Restricted workspace sandbox (`./workspace`) | Critical | `[DONE]` | None | Canonical path resolution, strict isolation inside `./workspace`, blocking `../` traversal. |
| **TASK-102** | Automatic pre-modification backups | High | `[DONE]` | TASK-101 | Store timestamped rollback files in `.aegis_backups/` before any patch is written. |
| **TASK-103** | Human-in-the-loop patch approval lifecycle | Critical | `[DONE]` | TASK-101 | Consequential actions require explicit approval; zero autonomous self-approval. |
| **TASK-104** | Command allowlist verification | Critical | `[DONE]` | TASK-103 | Only allowlisted test commands (`pytest`, `unittest`, `npm test`) can be executed with timeouts. |
| **TASK-105** | Persistent SQLite memory & keyword indexing | High | `[DONE]` | None | Persistent storage of preferences, facts, and context; keyword matching; sensitive secret filtering. |

---

## 9. Milestone 9: Tree-sitter Highlighting & Dense Semantic Retrieval (v0.9.0 — Planned)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-901** | Tree-sitter WebAssembly grammar integration | Medium | `[PLANNED]` | None | AST-based token coloring for deeper semantic highlighting. |
| **TASK-902** | Multi-file workspace diff staging viewer | High | `[PLANNED]` | None | Multi-tab diff viewer in workspace modal for complex refactorings. |
| **TASK-903** | Dense vector search via local embeddings | High | `[PLANNED]` | None | Embeddings stored in SQLite-vec alongside keyword matching. |


