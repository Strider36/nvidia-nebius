# Changelog

All notable changes to **Aegis AI** are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] — 2026-10-30

### Added
- **Unified Premium Design System Across Entire Application**:
  - Implemented mathematical typography scale in `:root` (`--font-size-2xs` through `--font-size-2xl`, `--line-height-tight`, `--line-height-normal`, `--line-height-relaxed`).
  - Implemented systematic spacing scale in `:root` (`--space-3xs` through `--space-2xl`) and elevation tokens (`--shadow-sm` through `--shadow-popover`).
  - Unified color tokens centrally: Obsidian canvas (`#0B0C0F`), Graphite sidebar (`#101116`), Secondary surface (`#15171D`), Elevated surface (`#1B1D25`), Platinum text (`#E6E4EC`), Slate text (`#A2A2AF`), Muted text (`#777986`), Electric Violet (`#A78BFA`), Violet hover (`#B9A5FF`), Hairline border (`#292B32`), Success (`#62C9A0`), Warning (`#E7B96A`), Error (`#F07878`).
- **Shared Component Foundation (7 Cohesive Views)**:
  - **Main Chat**: Refined message rows, unified action toolbars (Copy, Retry), and memory pills sharing identical token geometry and micro-transitions.
  - **Skills View**: Modernized `.skill-catalog-card` with `.btn-primary` activation actions, `.tool-tag` monospace badges, and structured typography hierarchy.
  - **Memory View**: Standardized `.tab-pill-bar`, elevated `.memory-card` containers, and flattened directive creation form (completely eliminating card-in-card nesting).
  - **Approvals View**: Upgraded `.approval-item-card` with `.status-pill` badges (`ready`, `pending`, `rejected`), syntax-highlighted diff boxes, and clear decision action groups.
  - **Workspace View**: Upgraded `.workspace-header-info`, SVG file explorer items (eliminating raw emoji glyphs), and refined `.file-preview-box` with monospace code typography.
  - **Audit View**: Standardized `.data-table` / `.audit-table` with sticky graphite header, alternating rows, monospace timestamps (`.mono-time`), and status pill indicators.
  - **Settings & Provider Diagnostics View**: Implemented dedicated `#modalSettings` modal dialog displaying active provider, model identifiers, loopback network interfaces (`127.0.0.1`), directory traversal guard invariants, and live connectivity diagnostics (`#btnRunDiagnostics`).
- **Pure Geometric SVG Close Buttons**:
  - Eliminated all raw HTML text character entities (`&times;`) across all modal headers, search inputs, and approval panels, replacing them with accessible, responsive SVG close icon buttons (`aria-label="Close modal"`).
- **Navigation Controls**:
  - Added dedicated Settings trigger `#btnOpenSettingsModal` to the sidebar footer and `#btnTopbarSettings` to the topbar for seamless configuration access from any view.
- **Automated Test Coverage**:
  - Added `test_frontend_unified_design_system_and_settings()` in `tests/test_frontend.py` verifying design tokens, shared components, SVG close buttons, and Settings modal.
  - Total automated tests passing: 56 Python tests + 11 Node JavaScript tests (100% pass rate).

### Changed
- Bumped application version to `0.7.0` in `app/__init__.py`, `pyproject.toml`, and documentation suite.

---

## [0.6.0] — 2026-10-30

### Added
- **Native Server-Sent Events (SSE) Token Streaming**:
  - Added `POST /api/chat/stream` endpoint returning `StreamingResponse(media_type="text/event-stream")` with anti-buffering headers.
  - Implemented `LLMService.generate_stream(...)` providing native chunked streaming for both local Ollama HTTP API (`stream: true`) and cloud OpenAI SDK (`stream=True`).
  - Maintained strict provider isolation: local Ollama streaming failures never trigger silent cloud fallback.
  - Implemented `AgentService.process_chat_stream(...)` delivering incremental SSE events:
    - Live tokens: `data: {"token": "...", "done": false}\n\n`
    - Final completion: `data: {"done": true, "conversation_id": "...", "assistant_message": "...", "pending_approvals": [...], "retrieved_memories": [...]}\n\n`
    - Sanitized errors: `data: {"error": "...", "done": true, ...}\n\n`
  - Refactored proposal extraction into `AgentService._parse_actions_and_format` ensuring 100% parity between streaming and non-streaming modes for `PROPOSE_PATCH`, `PROPOSE_COMMAND`, and `PROPOSE_TASK`.
- **Client-Side Incremental Token Renderer (`frontend/app.js`)**:
  - Implemented `ReadableStream` reader with `TextDecoder("utf-8")` parsing SSE chunks in real time.
  - Reusable streaming bubble helper `createStreamingMessageRow` with clean Obsidian-themed DOM structure.
  - Authentic blinking block cursor (`.streaming-cursor` with `@keyframes streamBlink`) and `.stream-content` presentation.
  - Seamless finalization: removes cursor upon completion, executes `renderSafeMarkdown`, highlights code syntax, and attaches action buttons (Copy, Retry).
- **Intelligent Viewport Auto-Scroll Lock**:
  - Automatically scrolls to the bottom if the user is already within 160px of the bottom.
  - Preserves scroll position without jumpiness if the user scrolls up to inspect previous code or thoughts.
- **Active Stream Cancellation & Generator Cleanup**:
  - Terminating stream via `#btnStop` or `Escape` key signals `AbortController` and halts the HTTP stream.
  - Backend generator catches `GeneratorExit` on client disconnection and persists partial response to SQLite with `*(Generation stopped by user)*`.
- **Automatic Fallback Protection**:
  - If `/api/chat/stream` fails or is blocked by network proxies, `app.js` automatically falls back to non-streaming `/api/chat`.
- **Expanded Automated Test Suite**:
  - Added unit and HTTP integration tests for SSE stream generation in `tests/test_chat.py`.
  - Added Ollama streaming tests in `tests/test_provider.py` and Cloud streaming tests in `tests/test_llm.py`.
  - Added frontend streaming assets verification in `tests/test_frontend.py`.
  - Total automated tests increased from 57 to 66 (55 Python + 11 JavaScript) with 100% pass rate.

### Changed
- Bumped application version to `0.6.0` in `app/__init__.py` and `pyproject.toml`.

---

## [0.5.0] — 2026-10-30

### Added
- **Obsidian, Graphite, Platinum & Electric Violet Design System**:
  - Replaced generic navy/cyan styling with a bespoke developer-focused identity.
  - Centralized surface tokens: Obsidian canvas (`#0B0C0F`), Graphite sidebar (`#101116`), elevated surfaces (`#15171D`, `#1B1D25`).
  - High-contrast Platinum typography (`#E6E4EC`), Slate secondary text (`#A2A2AF`), and muted captions (`#777986`) meeting WCAG AAA/AA standards.
  - Electric Violet accent palette (`#A78BFA`, `#B9A5FF`, `rgba(167, 139, 250, 0.12)`).
  - Crisp hairline borders (`#292B32`, `#3D414D`) and semantic state tokens (`#62C9A0` success, `#E7B96A` warning, `#F07878` error).
- **Physics-Based Motion System**:
  - Implemented cohesive motion physics tokens: `--ease-out: cubic-bezier(0.16, 1, 0.3, 1)`, `--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1)`.
  - Defined timing scale: `--duration-fast: 150ms`, `--duration-normal: 220ms`, `--duration-slow: 360ms`.
  - Added staggered entrance physics on prompt suggestion chips (`@keyframes chipEntrance`).
  - Added smooth fade-and-rise entrance on welcome hero composition (`@keyframes heroEntrance`).
  - Micro-interaction press scaling (`scale(0.98)`) on buttons and focus glow rings on input elements.
  - Comprehensive accessibility compliance with `@media (prefers-reduced-motion: reduce)`.
- **Pure Geometric SVG Iconography**:
  - Replaced all platform-dependent emoji glyphs (`📋`, `🔍`, `🐞`, `🧪`, `🧠`) with bespoke, uniform 1.75px stroke inline SVGs.
- **Design System & Motion Automated Test Suite**:
  - Added `test_frontend_obsidian_violet_design_system_and_motion` in `tests/test_frontend.py` verifying color tokens, motion variables, keyframes, and geometric SVGs.
- **Synchronized Documentation Suite**:
  - Reconciled and updated `PRD.md`, `README.md`, `ARCHITECTURE.md`, `IMPLEMENTATION_PLAN.md`, `TASKS.md`, and `TESTING.md` for version 0.5.0.

### Changed
- Bumped application version to `0.5.0` in `app/__init__.py` and `pyproject.toml`.
- Harmonized syntax highlighting token colors to Electric Violet (`#A78BFA`), Sage Mint (`#62C9A0`), Slate (`#777986`), and Sky (`#93C5FD`).

### Verification & Tests
- **57 total automated tests executed**: 57 passed, 0 failed.
  - 46 Python backend tests passed (`python -m pytest`).
  - 11 JavaScript frontend renderer tests passed (`node tests/test_markdown_renderer.js`).

---

## [0.4.0] — 2026-10-29

### Added
- **Premium Response Experience & Syntax Highlighting**:
  - Implemented zero-dependency multi-language syntax tokenizer (`highlightSyntax`) supporting **Python, JavaScript, TypeScript, Java, SQL, JSON, Bash, PowerShell, HTML/XML, CSS, YAML, and Markdown**.
  - Styled with dark-theme tokens (`.tok-keyword`, `.tok-string`, `.tok-comment`, `.tok-function`, `.tok-number`, `.tok-boolean`, `.tok-operator`, `.tok-type`, `.tok-attr`, `.tok-tag`).
  - Added code block chrome with detected language badge, horizontal scrolling, and dedicated copy button.
- **Resilient Safe Markdown Engine**:
  - Formatted headings (`#`, `##`, `###`), blockquotes, inline formatting (`**bold**`, `*italic*`, `` `code` ``), and arbitrarily nested lists (`-`, `*`, `1.`).
  - Responsive GitHub Flavored Markdown table parsing with alignment rules (`:---`, `:---:`, `---:`) enclosed in horizontal overflow wrappers (`.msg-table-wrapper`).
  - Safe URL sanitizer (`sanitizeUrl`) blocking `javascript:`, `vbscript:`, and `data:` schemes while allowing `http(s)://` and `mailto:`.
  - Unclosed code block auto-recovery preventing broken layouts during interrupted responses.
- **Message Action Bar & Toast Feedback**:
  - Added one-click **Copy response** button to copy complete assistant turns.
  - Added individual **Copy code** buttons for every code block.
  - Added clipboard fallback mechanism (`copyToClipboard`) using `document.execCommand('copy')` when `navigator.clipboard` is restricted or unavailable.
  - Added floating animated toast notifications (`#toastContainer`, `showToast`).
- **Client-Side Request Cancellation**:
  - Implemented true cancellation via `AbortController` bound to the `#btnStop` stop button and `Escape` key.
  - Cancelling immediately halts the in-flight HTTP request, resets composer controls, and displays `⏹️ Generation cancelled by user` without corrupting conversation history.
- **Automated Frontend Test Harness**:
  - Created Node.js test suite (`tests/test_markdown_renderer.js`) running 11 isolated unit tests against the client renderer using native `node:vm` and `node:assert`.
  - Added frontend asset and syntax token assertions to `tests/test_frontend.py`.
- **Complete Project Documentation Suite**:
  - Created comprehensive `PRD.md` with product vision, target personas, functional requirements, and provider behaviors.
  - Created `IMPLEMENTATION_PLAN.md` tracking completed milestones v0.1–v0.4 and future roadmap.
  - Created `TASKS.md` practical task tracker with task IDs, priority, and acceptance criteria.
  - Reconciled and updated `ARCHITECTURE.md`, `README.md`, and `TESTING.md`.

### Changed
- Bumped application version to `0.4.0` in `app/__init__.py` and `pyproject.toml`.
- Replaced code block placeholder format with `@@AEGIS-CODE-BLOCK-${idx}@@` to eliminate collision with markdown italic regex tokens.
- Added automatic CRLF-to-LF line ending normalization in `renderSafeMarkdown` to prevent Windows carriage return regex issues.
- Replaced DOM-dependent `escapeHtml` with isomorphic pure-string replacement for Node.js test harness compatibility.

### Verification & Tests
- **56 total tests executed**: 56 passed, 0 failed.
  - 45 Python backend tests passed (`python -m pytest`).
  - 11 JavaScript frontend renderer tests passed (`node tests/test_markdown_renderer.js`).

---

## [0.3.0] — 2026-10-29

### Added
- **ChatGPT-Inspired Minimalist Interface**: Transformed the frontend into a clean, dark AI chat experience with near-black (`#0d0d0d`) background, charcoal (`#171717`) sidebar, restrained cyan brand accents (`#06b6d4`), and modern typography (`Inter`, `Plus Jakarta Sans`, `JetBrains Mono`).
- **Collapsible Sidebar with Search & Date Grouping**:
  - Instant client-side conversation filtering via `#conversationSearchInput` with clear button.
  - Chronological date grouping (`Today`, `Yesterday`, `Previous 7 Days`, `Older`) with hover rename and delete controls.
  - Smooth collapsible desktop sidebar state (`Ctrl+[` shortcut) and mobile off-canvas drawer with touch backdrop overlay.
- **ChatGPT-Style Welcome Screen**:
  - Clean centered hero with headline `"How can I help you build today?"` and description `"Plan projects, understand code, debug problems, and improve your development workflow."`
  - Replaced bulky dashboard cards with 4 compact suggestion chips (`Plan a Project`, `Explain Code`, `Debug an Issue`, `Generate Tests`) that trigger prompts through the existing chat workflow.
- **Floating Rounded Message Composer**:
  - Centered reading column (`max-width: 48rem` / `768px`) with auto-resizing textarea (`min-height: 36px`, `max-height: 180px`), Enter-to-send, and Shift+Enter for newline.
  - Circular send button with loading spinner state and safety disclaimer.
- **Assistant Message Actions**:
  - Added one-click **Copy response** (`.btn-copy-response`) and **Retry** (`.btn-retry`) buttons below assistant turns.
  - Code syntax preservation with language tags, copy code buttons (`.btn-copy-code`), and horizontal scrolling.
- **Conversation Rename Support**:
  - Added `PATCH /api/conversations/{conversation_id}` backend endpoint with `AgentService.rename_conversation()`.
  - Added click-to-rename on the active session header and pencil icon in the conversation history list.
- **Responsive Mobile Layout**:
  - Off-canvas sidebar drawer for tablet/mobile viewports (`<= 768px`) with hamburger toggle and backdrop dismiss.
  - Viewport-safe padding with mobile safe-area inset handling (`env(safe-area-inset-bottom)`).

### Preserved
- Full backward compatibility for dual-provider inference (Local Ollama Nemotron 3.5 Bolt E4B + Cloud Nebius/OpenRouter).
- Unaltered developer tools: Skills, Memory, Approvals, Workspace Explorer, and Audit Trail.
- Unchanged human-in-the-loop security verification and diff safety cards (`.approval-task-card`, `.diff-box`).

### Verification & Tests
- **44 total tests executed**: 44 passed, 0 failed.
  - Added `test_frontend_chatgpt_redesign_elements` in `tests/test_frontend.py`.
  - Added `test_conversation_rename_endpoint` in `tests/test_chat.py`.

---

## [0.2.0] — 2026-10-29

### Added
- **Dual-Provider Inference Engine**: Added first-class support for local **NVIDIA Nemotron 3.5 Bolt E4B** via Ollama alongside existing cloud inference (Nebius Token Factory / OpenRouter).
- **Runtime Provider Switching**: Toggle active inference provider on-the-fly directly from the web interface or via `POST /api/provider` without restarting the server.
- **Provider Status API (`GET /api/provider`)**: Real-time status reporting on Ollama connectivity, installed models, and cloud credentials with non-leaking security assertions.
- **Provider-Aware Health Endpoint (`GET /api/health`)**: Extended health checks with non-blocking reachability verification and model tags for both local and cloud modes.
- **Top Bar Provider Switcher UI**: Compact toggle pill (`Local (Ollama)` / `Cloud`) with dynamic status dots (ready, offline, model_missing, unconfigured) and active model tag display.
- **Per-Request Provider Isolation**: Snapshotting of provider state per request to eliminate race conditions in concurrent multi-turn sessions.
- **Ollama Error Sanitization**: Specialized handling for HTTP 404 (model missing with pull recommendation), connection timeouts, socket errors, and malformed responses.
- **Provider Test Suite (`tests/test_provider.py`)**: 12 new comprehensive tests verifying payload structures, error paths, concurrent isolation, and anti-fallback invariants.

### Security
- **Strict Anti-Fallback Guarantee**: Enforced zero silent fallback between providers. A failure in local Ollama will never automatically route prompts or workspace code to cloud providers.
- **Secret Redaction**: Health and provider APIs strictly redact API keys and authentication tokens from all responses and log payloads.

### Changed
- `app/config.py`: Added `LLM_PROVIDER`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, and `OLLAMA_TIMEOUT` with thread-safe `_provider_lock`.
- `app/services/llm_service.py`: Extended `LLMService` with `_generate_ollama` and `_generate_cloud` unified under the `generate()` contract.
- `app/services/agent_service.py`: Updated `process_chat` to snapshot target provider per turn.
- `app/api/health.py`: Updated readiness calculations to verify active provider status.
- `frontend/index.html` & `frontend/styles.css`: Added compact provider switcher controls and obsidian theme styling.
- `frontend/app.js`: Added provider state management, real-time polling, and UI badge binding.
- `.env.example`: Added configuration instructions for Ollama and dual providers.
- `pyproject.toml` & `app/__init__.py`: Version bumped from 0.1.0 to 0.2.0.

### Verification & Tests
- **42 total tests executed**: 42 passed, 0 failed.
  - `tests/test_provider.py`: 12 passed
  - `tests/test_approvals.py`: 2 passed
  - `tests/test_audit.py`: 2 passed
  - `tests/test_chat.py`: 5 passed
  - `tests/test_frontend.py`: 3 passed
  - `tests/test_health.py`: 2 passed
  - `tests/test_llm.py`: 4 passed
  - `tests/test_memory.py`: 4 passed
  - `tests/test_projects.py`: 2 passed
  - `tests/test_workspace.py`: 6 passed

---

## [0.1.0] — 2026-10-29

### Added
- Initial release of Aegis AI with persistent local SQLite memory, restricted safe workspace sandbox, human approval engine, and Nebius Token Factory inference.
