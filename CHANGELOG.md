# Changelog

All notable changes to **Aegis AI** are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
