# Aegis AI — Implementation Plan & Roadmap

**Current Release:** v0.8.2  
**Baseline Date:** 2026-10-30  
**Status:** Milestones 1–10 Completed; Milestone 11 Planned  

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
|  MILESTONE 3 (v0.3.0) - Interface Layout & Conversation Architecture [COMPLETED]     |
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
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|  MILESTONE 5 (v0.5.0) - Obsidian/Violet Theme, Motion System & SVGs [COMPLETED]       |
|  - Obsidian (#0B0C0F), Graphite (#101116), Platinum (#E6E4EC), Violet (#A78BFA)      |
|  - Cohesive motion physics system (--ease-out, --duration-fast/normal/slow)          |
|  - Pure geometric SVG iconography (eliminated all platform-dependent emojis)          |
|  - Micro-interactions, staggered entrance physics, and reduced-motion mode            |
|  - 57 automated tests (46 Python + 11 JavaScript) with 100% pass rate                |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|  MILESTONE 6 (v0.6.0) - Native Token Streaming & Advanced Tooling [COMPLETED]        |
|  - Server-Sent Events (SSE) streaming endpoint (/api/chat/stream)                     |
|  - Real-time token streaming from local Ollama & Cloud OpenAI SDK                     |
|  - Client-side ReadableStream reader with authentic blinking cursor                   |
|  - Auto-scroll lock: auto-scrolls at bottom (<=160px), preserves position on scroll   |
|  - Real streaming cancellation (AbortController halting stream & generator)           |
|  - 66 automated tests (55 Python + 11 JavaScript) with 100% pass rate                |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|  MILESTONE 7 (v0.7.0) - Unified Premium Design System Across Application [COMPLETED]  |
|  - Mathematical typography scale (--font-size-2xs through --font-size-2xl)            |
|  - Systematic spacing scale (--space-3xs through --space-2xl) and elevation tokens    |
|  - Shared component foundation (.btn-*, .status-pill, .data-table, .empty-state)      |
|  - Standardized modal subsystem across Skills, Memory, Approvals, Workspace, Audit     |
|  - Pure geometric SVG close buttons (.btn-close) eliminating raw '&times;' glyphs     |
|  - Zero card-in-card nesting: flattened surfaces in modals and forms                  |
|  - Dedicated Settings & Provider Diagnostics dialog (#modalSettings)                  |
|  - 67 automated tests (56 Python + 11 JavaScript) with 100% pass rate                |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|  MILESTONE 8 (v0.8.0) - Hermes Agent Backend Integration [COMPLETED]                  |
|  - Subprocess adapter (HermesService) invoking local Hermes Agent CLI (v0.22.5)       |
|  - Support for local NVIDIA Nemotron via Ollama (http://127.0.0.1:11434/v1)          |
|  - Sandboxed execution strictly inside ./workspace (--in <workspace_path>)            |
|  - Unsupervised internal tools suppressed (--toolsets "")                             |
|  - Human approval workflow preserved for patches, commands, and tasks                 |
|  - JSONL streaming token parser integrated with native SSE (/api/chat/stream)         |
|  - Strict anti-fallback invariant: local Ollama failures never failover to cloud     |
|  - Frontend Agent Mode switcher & Hermes diagnostic settings card                     |
|  - 76 automated tests (65 Python + 11 JavaScript) with 100% pass rate                |
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

### Milestone 3: Interface Layout & Conversation Architecture (v0.3.0) — [COMPLETED]
- [x] Collapsible history sidebar with real-time text filter and date grouping.
- [x] Centered reading column and floating composer with auto-expansion up to 180px.
- [x] Conversation session renaming via `PATCH /api/conversations/{id}`.
- [x] Responsive layout with off-canvas drawer and backdrop dismiss for mobile devices.

### Milestone 4: Premium Response Experience & Complete Docs (v0.4.0) — [COMPLETED]
- [x] Zero-dependency syntax highlighter supporting 12+ languages.
- [x] Resilient Markdown parser supporting headings, quotes, tables, and arbitrarily nested lists.
- [x] Safe URL sanitization allowing only `http://`, `https://`, and `mailto:` schemes.
- [x] Code block recovery for unclosed or streaming code fences.
- [x] Assistant actions: one-click copy response, copy code with legacy `execCommand` fallback, idempotent retry.
- [x] Request cancellation pipeline using native `AbortController` bound to `#btnStop` and `Escape`.
- [x] Node.js test harness (`tests/test_markdown_renderer.js`) and expanded `tests/test_frontend.py`.

### Milestone 5: Obsidian/Violet Theme, Motion System & SVGs (v0.5.0) — [COMPLETED]
- [x] Full Obsidian, Graphite, Platinum, and Electric Violet design system (`#0B0C0F`, `#101116`, `#15171D`, `#1B1D25`, `#E6E4EC`, `#A78BFA`).
- [x] Centralized CSS variable tokens eliminating scattered hardcoded colors.
- [x] Physics-based motion system (`--ease-out`, `--duration-fast/normal/slow`).
- [x] Staggered entrance animations on prompt suggestion chips and welcome composition.
- [x] Micro-interaction button pressed scaling (`scale(0.98)`).
- [x] Pure geometric SVG iconography replacing all platform-dependent emoji glyphs.
- [x] Dedicated test suite for design tokens and motion keyframes (`test_frontend.py`).
- [x] 57 automated tests passed with 100% success rate.

---

### Milestone 6: Native Token Streaming & Advanced Tooling (v0.6.0) — [COMPLETED]
- [x] Backend SSE Streaming Endpoint: `POST /api/chat/stream` delivering `text/event-stream`.
- [x] Ollama Native Streaming: Yielding chunks via Ollama's HTTP API (`stream: true`).
- [x] Cloud Native Streaming: Yielding delta chunks from the OpenAI SDK client (`stream=True`).
- [x] Client-side Incremental Token Renderer in `frontend/app.js`: Consuming `ReadableStream` with `TextDecoder`.
- [x] Authentic blinking block cursor (`.streaming-cursor` with `@keyframes streamBlink`) and `.stream-content`.
- [x] Viewport Auto-Scroll Lock: Auto-scrolling when user is within 160px of bottom, freezing scroll position if user scrolls up.
- [x] Real Streaming Cancellation: Terminating the active stream and backend generator on `#btnStop` click or `Escape` key (`AbortController`).
- [x] Non-Streaming Fallback Preservation: Keeping `POST /api/chat` fully working and backward-compatible.
- [x] 66 automated tests (55 Python + 11 JavaScript) with 100% pass rate.

---

### Milestone 7: Unified Premium Design System Across Application (v0.7.0) — [COMPLETED]
- [x] Centralized Design Tokens: Mathematical typography scale (`--font-size-2xs` to `--font-size-2xl`), spacing scale (`--space-3xs` to `--space-2xl`), elevation shadows.
- [x] Shared Component Foundation: Standardized `.btn-*` styles, `.status-pill` indicators with live glowing dots, `.data-table` and `.audit-table` with sticky headers, `.empty-state` with SVG icons.
- [x] Standardized Modal Subsystem: All 6 dialogs (Skills, Memory, Approvals, Workspace, Audit, Settings) share `.modal-title-group`, SVG title icons, subtitle descriptions, and `.btn-close` geometric SVG buttons.
- [x] Elimination of Legacy Glyphs: Completely eliminated raw `&times;` entities across all modals, search inputs, and approval cards.
- [x] Surface De-Cluttering: Flattened Add Memory form, eliminating nested card-in-card visual noise while preserving high contrast and clear visual hierarchy.
- [x] Dedicated Settings & Provider Diagnostics View (`#modalSettings`): Detailed cards for Active Inference Engine, Network & Privacy Boundaries, Data Persistence & Sandbox, plus interactive diagnostics probe (`#btnRunDiagnostics`).
- [x] Dynamic View Modernization: Updated `renderModalProjects`, `loadTasksForProject`, `loadMemories`, `loadSkillsCatalog`, `loadWorkspaceBrowser`, `loadAuditTrail`, `loadModalApprovals` to render standard `.status-pill` badges and monospace timestamps.
- [x] Frontend Regression Suite: Added `test_frontend_unified_design_system_and_settings()` in `tests/test_frontend.py`.
- [x] 67 automated tests (56 Python + 11 JavaScript) with 100% pass rate.

---

### Milestone 8: Hermes Agent Optional Backend Integration (v0.8.0) — [COMPLETED]
- [x] Host Environment Discovery: Located Hermes CLI at `C:\Users\jayan\AppData\Local\hermes\bin\hermes.exe` (`Hermes Agent v0.22.5`).
- [x] Ollama Nemotron Compatibility: Validated invocation against local Ollama endpoint (`http://127.0.0.1:11434/v1`) using model `nemotron-3.5-bolt:e4b`.
- [x] Subprocess Adapter (`HermesService`): Built secure non-interactive CLI wrapper passing queries via temporary files and capturing stdout.
- [x] JSONL Streaming Protocol: Implemented real-time token generator decoding `{"type": "text", "text": "..."}` events into Aegis SSE chunks (`POST /api/chat/stream`).
- [x] Workspace Sandboxing: Confined Hermes execution directory to `./workspace` (`--in <workspace_path>`).
- [x] Autonomous Tool Suppression: Disabled rogue external tools by passing `--toolsets ""`.
- [x] Human Approval Interception: Preserved the Aegis approval pipeline by extracting `<<<PROPOSE_PATCH>>>` and `<<<PROPOSE_COMMAND>>>` tags from Hermes output into SQLite `pending_approvals`.
- [x] Anti-Fallback Invariant: Maintained strict local isolation on Ollama failures without silent cloud failover.
- [x] Frontend Controls & Status: Added topbar Agent Mode switcher (`#agentModeSwitcher`) and Hermes status card in Settings modal (`#settingsHermesCard`).
- [x] Diagnostic Route: Added `GET /api/hermes/status` checking binary presence, version, and provider readiness.
- [x] Automated Test Suite: Added `tests/test_hermes.py` (8 test cases) and frontend regression test in `tests/test_frontend.py`.
- [x] 76 automated tests (65 Python + 11 JavaScript) with 100% pass rate.

---

### Milestone 9: Full-System Optimization, Reliability & Verification (v0.8.1) — [COMPLETED]
- [x] Full Repository Audit: Audited backend routers, SQLite pragmas, subprocess execution, Hermes integration, and frontend client.
- [x] FastAPI Version Synchronization: Bound `FastAPI(..., version=__version__)` to `app.__version__` (`0.8.1`), eliminating version drift across API docs.
- [x] Subprocess Windows Character Encoding Resilience: Added explicit `encoding="utf-8", errors="replace"` across `hermes_service.py` and `workspace_service.py` to prevent Windows `cp1252` encoding crashes on LLM emoji outputs.
- [x] Subprocess Timeout & Stream Cleanup Hardening: Implemented safe communicate timeouts and client disconnect tracking (`GeneratorExit`).
- [x] Workspace Sandboxing & Backup Verification: Verified path traversal defenses, symlink resolution, `.aegis_backups` automated pre-modification snapshots, and allowlisted test execution inside sandboxed `./workspace`.
- [x] End-to-End Test Suite: Added `tests/test_e2e_live.py` (4 tests) covering metadata sync, secret-free provider inspection, and complete multi-step human approval lifecycle.
- [x] 80 automated tests (69 Python + 11 JavaScript) with 100% pass rate.

---

### Milestone 10: Hermes Autonomous Execution & Safety Boundaries (v0.8.2) — [COMPLETED]
- [x] Root Cause Audit & Smallest Reliable Fix: Identified that Hermes was invoked with `--toolsets ""` and instructions forced `<<<PROPOSE_PATCH>>>`/`<<<PROPOSE_COMMAND>>>`, which `agent_service.py` unconditionally intercepted into SQLite pending approvals queue regardless of action safety.
- [x] Dual Execution Modes Architecture: Added `ExecutionMode` enum (`autonomous`, `supervised`) in `app/models.py` and `app/config.py`, defaulting Hermes to `autonomous` and Native Aegis to `supervised`.
- [x] Workspace File Tree Context Injection: Injected `./workspace` directory structure into system directives so Hermes can inspect and reason about existing project files with zero approval prompts.
- [x] Supervisor-Mediated Autonomous Execution: Implemented `approval_service.execute_action_autonomously()`. In autonomous mode, routine patches (`<<<PROPOSE_PATCH>>>`), safe commands, and task items execute automatically with pre-modification backups created in `.aegis_backups`, approval records set to `SUCCEEDED`, and audit log entries recorded.
- [x] Expanded Non-Destructive Allowlisted Commands: Broadened allowlist to include `pytest`, `python -m pytest`, `python -m unittest`, `npm test`, `node --test`, `ruff`, `flake8`, `mypy`, `git status`, `git diff`, and `python -m py_compile`.
- [x] Multi-Step Autonomous Error Recovery: When an allowlisted test or build command fails in autonomous mode, the supervisor captures stdout/stderr and automatically prompts Hermes to analyze the failure and apply a fix.
- [x] Essential Safety Boundaries:
  - Deletions (`ActionType.FILE_DELETE`, `<<<PROPOSE_DELETE>>>`) strictly require human approval.
  - Path traversal attempts (`../`, absolute paths outside `./workspace`) are rejected with `WorkspaceSecurityError` and security audit log entries.
  - Access to credentials or secrets (`.env`, `.git/`, SSH keys) is blocked at the supervisor gateway.
  - Destructive or chained commands (`&&`, `;`, `|`, `rm`) are strictly blocked.
- [x] Frontend Mode Controls: Added `#executionModeSwitcher` (`#btnModeAutonomous`, `#btnModeSupervised`) in topbar and `#settingsHermesMode` in Settings modal.
- [x] Verification of 10 Required Scenarios: Added 10 explicit test scenarios in `tests/test_hermes.py` covering inspection, file creation, bug fixes, running tests, multi-file edits, deletion approval, path traversal blocking, secret blocking, supervised mode fallback, and native Aegis isolation.
- [x] 89 automated tests (78 Python + 11 JavaScript) with 100% pass rate.

---

## 3. Planned Milestones & Remaining Work

### Milestone 11: Tree-sitter Highlighting & Dense Semantic Retrieval (v0.9.0) — [PLANNED]
- **Objective**: Enhance code AST inspection and integrate dense embedding vector search.
- **Tasks**:
  1. *Tree-sitter WASM Highlighting*: Optional WebAssembly-based AST highlighting for deeper semantic colorization.
  2. *Multi-File Workspace Diffs*: Interactive multi-tab diff viewer for large refactorings touching dozens of files.
  3. *Dense Semantic Retrieval*: Local SQLite-vec integration for dense retrieval in place of keyword-based memory matching.

---

## 4. Verification & Quality Gates

Every milestone must satisfy the following strict quality gates:
1. **Automated Unit Tests**: All Python tests must pass (`pytest` exit code 0).
2. **Frontend Markdown Tests**: All Node.js tests must pass (`node tests/test_markdown_renderer.js` exit code 0).
3. **Zero Deprecation / Syntax Errors**: Clean execution with zero unhandled exceptions.
4. **Offline Execution**: The test suite must run without active internet access or cloud API credentials.
5. **Human Approval Intact**: Patches and commands must never execute automatically without an explicit human approval record in SQLite.
6. **Documentation Synchronization**: All version numbers, API endpoints, and configuration examples must match across `PRD.md`, `README.md`, `ARCHITECTURE.md`, `TESTING.md`, `IMPLEMENTATION_PLAN.md`, `TASKS.md`, and `CHANGELOG.md`.
