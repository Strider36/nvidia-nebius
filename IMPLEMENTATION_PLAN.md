# Aegis AI — Implementation Plan & Roadmap

**Current Release:** v0.4.0  
**Baseline Date:** 2026-10-29  
**Status:** Milestones 1–4 Completed; Milestone 5 Planned  

---

## 1. Executive Implementation Strategy

Aegis AI uses an incremental, additive engineering methodology designed to deliver production stability, developer ergonomics, and strict security invariants without breaking existing contracts.

```
+---------------------------------------------------------------------------------------+
|  MILESTONE 1 (v0.1.0) - Core Security & Workspace Sandboxing [COMPLETED]              |
|  - Workspace path canonicalization & traversal protection                             |
|  - Human approval workflow for patches & allowlisted test runner commands              |
|  - SQLite persistent memory, projects, and immutable audit logs                       |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|  MILESTONE 2 (v0.2.0) - Dual-Provider Inference & Isolation [COMPLETED]               |
|  - Local Ollama integration (NVIDIA Nemotron 3.5 Bolt E4B)                            |
|  - Thread-safe runtime provider switching without server restart                      |
|  - Strict anti-fallback guarantee (no silent data routing to cloud)                   |
|  - Per-request provider snapshotting to prevent multi-turn race conditions             |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|  MILESTONE 3 (v0.3.0) - ChatGPT-Inspired Interface Redesign [COMPLETED]              |
|  - Obsidian dark theme (#0d0d0d / #171717) with restrained cyan branding (#06b6d4)    |
|  - Collapsible sidebar with real-time conversation search and date grouping           |
|  - Centered reading column (48rem) with auto-resizing floating composer               |
|  - Off-canvas drawer and full responsive viewport support for mobile/tablet           |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|  MILESTONE 4 (v0.4.0) - Premium Response Experience & Complete Docs [COMPLETED]       |
|  - Zero-dependency multi-language syntax highlighter (12+ languages)                  |
|  - Robust GFM Markdown engine (nested lists, table wrappers, safe URL sanitization)   |
|  - Action controls: copy response, copy code with fallback, retry, toast alerts       |
|  - Client-side request cancellation via AbortController (#btnStop & Esc)              |
|  - Node.js + pytest test suites (56 total tests) & six-core documentation suite       |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|  MILESTONE 5 (v0.5.0) - Native Token Streaming & Advanced Tooling [PLANNED]          |
|  - Server-Sent Events (SSE) streaming endpoint (/api/chat/stream)                     |
|  - Incremental response token rendering with auto-scroll lock preservation             |
|  - Multi-file unified diff staging viewer in workspace tab                            |
|  - Dense semantic retrieval via SQLite-vec / local embedding models                   |
+---------------------------------------------------------------------------------------+
```

---

## 2. Completed Milestones (Detailed Breakdown)

### Milestone 1: Core Foundation & Safe Sandbox (v0.1.0) — [COMPLETED]
- [x] Sandboxed workspace root (`./workspace`) with path canonicalization.
- [x] Path traversal rejection (`../`, hidden system files, absolute host paths).
- [x] Automatic pre-modification backup system in `.aegis_backups/`.
- [x] Human approval lifecycle (`PROPOSED -> PENDING_APPROVAL -> APPROVED -> EXECUTING -> SUCCEEDED / FAILED`).
- [x] Command allowlist validation (`pytest`, `python -m unittest`, `npm test`).
- [x] SQLite relational schema for memories, conversation sessions, approvals, and audit trail.
- [x] Built-in developer skills: Project Planner, Code Explainer, Debugger, Test Writer.

### Milestone 2: Dual-Provider Inference & Anti-Fallback Invariant (v0.2.0) — [COMPLETED]
- [x] Local Ollama HTTP client communicating with `http://127.0.0.1:11434`.
- [x] Cloud client with OpenAI-compatible endpoint supporting Nebius Token Factory / OpenRouter.
- [x] Runtime provider toggle via `POST /api/provider` and top navigation switch.
- [x] Non-blocking provider reachability probe with strict 2-second timeout.
- [x] Thread-safe `_provider_lock` and per-request provider snapshotting in `AgentService`.
- [x] Zero silent fallback invariant: guaranteed local data isolation on Ollama failure.
- [x] Comprehensive provider unit test suite (`tests/test_provider.py`).

### Milestone 3: ChatGPT-Inspired Interface Redesign (v0.3.0) — [COMPLETED]
- [x] Obsidian & charcoal visual hierarchy (`#0d0d0d`, `#171717`, `#212121`, `#06b6d4`).
- [x] Collapsible history sidebar with real-time text filter and date grouping.
- [x] ChatGPT-style welcome hero with 4 starter suggestion chips.
- [x] Floating, centered message composer with auto-expansion up to 180px.
- [x] Conversation session renaming via `PATCH /api/conversations/{id}`.
- [x] Responsive layout with off-canvas drawer and backdrop dismiss for mobile devices.

### Milestone 4: Premium Response Experience & Documentation (v0.4.0) — [COMPLETED]
- [x] Zero-dependency syntax highlighter supporting 12+ languages (Python, JS, TS, Java, SQL, JSON, Bash, PowerShell, HTML/XML, CSS, YAML, Markdown).
- [x] Resilient Markdown parser supporting headings, quotes, tables, and arbitrarily nested lists.
- [x] Safe URL sanitization allowing only `http://`, `https://`, and `mailto:` schemes.
- [x] Code block recovery for unclosed or streaming code fences.
- [x] Assistant actions: one-click copy response, copy code with legacy `execCommand` fallback, idempotent retry.
- [x] Toast notification system for clear user feedback.
- [x] Request cancellation pipeline using native `AbortController` bound to `#btnStop` and `Escape`.
- [x] Node.js test harness (`tests/test_markdown_renderer.js`) and expanded `tests/test_frontend.py`.
- [x] Six-core documentation suite and version increment to 0.4.0.

---

## 3. Planned Milestones & Remaining Work

### Milestone 5: Native Token Streaming & Advanced Tooling (v0.5.0) — [PLANNED]
- **Objective**: Deliver real-time incremental token streaming without breaking the existing request/response contract.
- **Tasks**:
  1. *Backend SSE Endpoint*: Implement `POST /api/chat/stream` using FastAPI `StreamingResponse` and Ollama streaming API (`stream: true`).
  2. *Cloud Streaming*: Stream chunks from OpenAI-compatible cloud client asynchronously.
  3. *Client-side Incremental Renderer*: Buffer incoming tokens, update the active message DOM node, and run lightweight syntax highlighting without full-document layout shift.
  4. *Smart Auto-Scroll*: Auto-scroll downwards while user is at the bottom of the viewport; freeze scroll position if user scrolls up to review prior content.
  5. *Streaming Cancellation*: Terminate backend generation immediately upon receiving client abort signal.
  6. *Fallback Preservation*: Retain `/api/chat` non-streaming endpoint for CLI and low-bandwidth use cases.

### Milestone 6: Semantic Vector Memory & Multi-File Diffs (v0.6.0) — [PLANNED]
- **Objective**: Enhance contextual recall and support large-scale refactorings.
- **Tasks**:
  1. *Local Embeddings*: Integrate SQLite-vec with lightweight local embedding models (e.g., `all-MiniLM-L6-v2`) for dense semantic retrieval.
  2. *Multi-File Patch Staging*: Interactive multi-file tabbed diff interface in the UI allowing partial file staging and individual approvals.
  3. *Git Integration*: Direct Git commit creation from approved patch sets with automated conventional commit messages.

---

## 4. Task Dependencies & Planned Order

```
[M4 Completed] v0.4.0 Baseline
       │
       ▼
[Task 5.1] FastAPI StreamingResponse Prototype (/api/chat/stream)
       │
       ▼
[Task 5.2] Ollama HTTP Async Generator Integration
       │
       ▼
[Task 5.3] Nebius/OpenRouter Async Streaming Generator Integration
       │
       ▼
[Task 5.4] Client EventSource / Fetch ReadableStream Consumer in frontend/app.js
       │
       ▼
[Task 5.5] Smart Viewport Auto-Scroll Lock Engine
       │
       ▼
[Task 5.6] Regression Test Suite for Streaming & Abort Mechanics
```

---

## 5. Risk Assessment & Mitigation

| Identified Risk | Severity | Likelihood | Mitigation Strategy |
|---|:---:|:---:|---|
| **Layout Shift During Token Streaming** | Medium | Medium | Render plain text during high-velocity token receipt; apply full syntax tokenization during brief pauses (debounce 80ms) or upon stream completion. |
| **Silent Cloud Fallback Vulnerability** | High | Low | Hardcoded invariant in `LLMService.generate()`: if provider is `'ollama'`, cloud branch is unreachable by design. Validated by 12 tests in `test_provider.py`. |
| **Clipboard Permission Denial in Browsers** | Low | Medium | Automatic fallback to `document.createElement('textarea')` with `document.execCommand('copy')` when `navigator.clipboard` is unavailable or denied. |
| **XSS via Malformed Markdown Links** | High | Low | Strict regex protocol allowlist (`/^(https?:\/\/|mailto:)/i`) rejecting `javascript:`, `vbscript:`, and `data:` URIs. |
| **Concurrent File Modification Conflicts** | Medium | Low | Workspace manager compares SHA-256 hashes and modification timestamps before applying patches, raising conflict warnings if files change out-of-band. |

---

## 6. Verification & Quality Gates

Every milestone must satisfy the following strict quality gates before merging into the main branch:
1. **Automated Unit Tests**: All Python tests must pass (`pytest` exit code 0).
2. **Frontend Markdown Tests**: All Node.js tests must pass (`node tests/test_markdown_renderer.js` exit code 0).
3. **Zero Deprecation / Syntax Errors**: Clean execution with zero unhandled exceptions or critical lint errors.
4. **Offline Execution**: The test suite must run without active internet access or cloud API credentials.
5. **Human Approval Intact**: Patches and commands must never execute automatically without an explicit human approval record in SQLite.
6. **Documentation Synchronization**: All version numbers, API endpoints, and configuration examples must match across `PRD.md`, `README.md`, `ARCHITECTURE.md`, `TESTING.md`, `IMPLEMENTATION_PLAN.md`, `TASKS.md`, and `CHANGELOG.md`.
