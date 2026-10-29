# Aegis AI — Task Tracker & Backlog

**Version Baseline:** 0.6.0  
**Last Updated:** 2026-10-30  
**Status Key:**  
- `[DONE]` Completed, verified with automated tests, and documented.
- `[IN_PROGRESS]` Currently active development.
- `[PLANNED]` Backlog item scheduled for upcoming release.

---

## 1. Milestone 5: Obsidian/Violet Theme, Motion System & SVGs (v0.5.0 — Completed)

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

## 2. Milestone 4: Premium Response Experience & Complete Documentation (v0.4.0 — Completed)

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

## 3. Milestone 3: Interface Layout & Conversation Architecture (v0.3.0 — Completed)

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

## 4. Milestone 2: Dual-Provider Inference & Anti-Fallback Invariant (v0.2.0 — Completed)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-201** | Local Ollama HTTP client integration | Critical | `[DONE]` | None | Async HTTP requests to `http://127.0.0.1:11434/api/chat` with NVIDIA Nemotron 3.5 Bolt E4B support. |
| **TASK-202** | Cloud provider integration (Nebius/OpenRouter) | Critical | `[DONE]` | None | OpenAI SDK compatible client using `NEBIUS_BASE_URL` and `NEBIUS_MODEL_ID`. |
| **TASK-203** | Thread-safe runtime provider switching | High | `[DONE]` | TASK-201, 202 | Thread-safe `_provider_lock` and `POST /api/provider` allowing dynamic switching without restart. |
| **TASK-204** | Non-blocking provider reachability probe | Medium | `[DONE]` | TASK-201 | Query `/api/tags` with strict 2.0s timeout to prevent server boot hang when Ollama is offline. |
| **TASK-205** | Per-request provider snapshotting in AgentService | Critical | `[DONE]` | TASK-203 | Snapshot provider choice per request to eliminate race conditions in concurrent multi-turn chats. |
| **TASK-206** | Anti-fallback invariant verification | Critical | `[DONE]` | TASK-205 | 12 tests in `tests/test_provider.py` confirming zero cloud fallback on Ollama failure or timeout. |

---

## 5. Milestone 1: Core Foundation & Safe Sandbox (v0.1.0 — Completed)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-101** | Restricted workspace sandbox (`./workspace`) | Critical | `[DONE]` | None | Canonical path resolution, strict isolation inside `./workspace`, blocking `../` traversal. |
| **TASK-102** | Automatic pre-modification backups | High | `[DONE]` | TASK-101 | Store timestamped rollback files in `.aegis_backups/` before any patch is written. |
| **TASK-103** | Human-in-the-loop patch approval lifecycle | Critical | `[DONE]` | TASK-101 | Consequential actions require explicit approval; zero autonomous self-approval. |
| **TASK-104** | Command allowlist verification | Critical | `[DONE]` | TASK-103 | Only allowlisted test commands (`pytest`, `unittest`, `npm test`) can be executed with timeouts. |
| **TASK-105** | Persistent SQLite memory & keyword indexing | High | `[DONE]` | None | Persistent storage of preferences, facts, and context; keyword matching; sensitive secret filtering. |

---

## 6. Milestone 6: Native Token Streaming & Advanced Tooling (v0.6.0 — Completed)

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

## 7. Milestone 7: Tree-sitter Highlighting & Dense Semantic Retrieval (v0.7.0 — Planned)

| Task ID | Description | Priority | Status | Dependencies | Acceptance Criteria |
|---|---|:---:|:---:|---|---|
| **TASK-701** | Tree-sitter WebAssembly grammar integration | Medium | `[PLANNED]` | None | AST-based token coloring for deeper semantic highlighting. |
| **TASK-702** | Multi-file workspace diff staging viewer | High | `[PLANNED]` | None | Multi-tab diff viewer in workspace modal for complex refactorings. |
| **TASK-703** | Dense vector search via local embeddings | High | `[PLANNED]` | None | Embeddings stored in SQLite-vec alongside keyword matching. |

