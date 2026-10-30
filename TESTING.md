# Aegis AI — Comprehensive Testing Guide & Verification Suite

**Version:** 0.8.2  
**Last Updated:** 2026-10-30  
**Status:** 100% Passing (89/89 Automated Tests)  

---

## 1. Testing Strategy & Principles

All unit, integration, and security tests in Aegis AI adhere to five strict testing principles:
1. **Deterministic & Offline**: Tests execute without internet access. Cloud endpoints are mocked via OpenAI client fixtures, and local Ollama calls are mocked via `httpx` transport fixtures.
2. **Persistent DB Isolation**: Each test run uses an isolated in-memory or temporary throwaway SQLite database (`tempfile.TemporaryDirectory`) ensuring zero state leakage between tests.
3. **Dual-Stack Verification**: Tests validate both the Python backend application (via `pytest` and `fastapi.testclient.TestClient`) and the client-side JavaScript rendering engine (via Node.js `node:vm` harness).
4. **Design System & Invariant Regression**: Dedicated assertions confirm the presence of all centralized Obsidian & Electric Violet tokens, mathematical typography, spacing tokens, shared component foundations (`.btn-*`, `.status-pill`, `.data-table`, `.empty-state`), standardized modal subsystem, geometric SVG iconography, and SSE streaming assets.
5. **Anti-Fallback & Security Checks**: Automated assertions verify that local inference failures (both via direct Ollama and Hermes Agent) never trigger silent cloud fallbacks, path traversal attempts are rejected, and secrets are redacted from logs.

---

## 2. Test Environment Requirements

- **Operating System**: Windows 11, Linux (Ubuntu 22.04+), or macOS (Sonoma+).
- **Python Runtime**: Python 3.11, 3.12, 3.13, or 3.14.
- **Node.js Runtime**: Node.js v18.0.0+ (verified on v24.19.0) with zero external `npm` dependencies (uses native `node:assert` and `node:vm`).

### Install Test Dependencies
```bash
pip install -r requirements.txt
```

---

## 3. Test Suites & Coverage Breakdown

### 3.1 Python Backend Test Suite (`pytest` — 78 Tests)

| Test Module | Focus Area | Tested Invariants | Test Count |
|---|---|---|:---:|
| [`tests/test_e2e_live.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_e2e_live.py) | End-to-End Integration & Lifecycle | Application metadata & versioning sync, provider status without secret leakage, Hermes binary detection, and complete multi-step human approval lifecycle (propose patch -> pending status -> approve -> write sandbox file -> create backup in `.aegis_backups` -> record audit log) | 4 |
| [`tests/test_hermes.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_hermes.py) | Hermes Agent Backend & Autonomous Execution | Subprocess command composition, Ollama Nemotron integration, Cloud provider integration, non-streaming generation, JSONL streaming generator, client cancellation cleanup, anti-fallback invariant enforcement, chat route integration with proposal extraction into SQLite approvals, **plus 10 explicit autonomous execution & safety scenario tests** | 17 |
| [`tests/test_provider.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_provider.py) | Dual-Provider Inference | Ollama HTTP payload, streaming tokens (`stream: true`), 404 model missing, timeouts, connection errors, runtime switching, per-request isolation, anti-fallback invariant | 13 |
| [`tests/test_llm.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_llm.py) | Cloud Provider Client | OpenAI SDK compatibility, incremental token streaming (`stream=True`), auth errors, quota limits, unconfigured fallback | 7 |
| [`tests/test_chat.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_chat.py) | Chat Orchestration & SSE Streaming | Session history, memory context injection, proposal parsing (`<<<PROPOSE_PATCH>>>`, `<<<PROPOSE_COMMAND>>>`, `<<<PROPOSE_TASK>>>`), `/api/chat/stream` SSE tokens and completion, conversation rename endpoint | 10 |
| [`tests/test_approvals.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_approvals.py) | Approval Lifecycle | State machine transitions (`PROPOSED -> PENDING_APPROVAL -> APPROVED -> EXECUTING -> SUCCEEDED / REJECTED`), execution safety | 2 |
| [`tests/test_workspace.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_workspace.py) | Workspace Sandboxing | Path canonicalization, traversal blocking (`../`), unified diff computation, timestamped pre-modification backups | 6 |
| [`tests/test_memory.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_memory.py) | Persistent SQLite Memory | Memory CRUD, keyword index retrieval, secret shield blocking credentials at gateway | 4 |
| [`tests/test_projects.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_projects.py) | Projects & Backlog | Project creation, milestone task tracking, status updates | 2 |
| [`tests/test_health.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_health.py) | Health & Readiness | Health probe payload, non-blocking DB and provider connectivity, secret non-leakage | 2 |
| [`tests/test_audit.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_audit.py) | Audit Trail Persistence | Audit logging to SQLite, automatic secret token scrubbing in logs | 2 |
| [`tests/test_frontend.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_frontend.py) | Static Assets & UI | Asset serving (`index.html`, `styles.css`, `app.js`), suggestion chips, `#btnStop`, `#toastContainer`, `highlightSyntax`, `.tok-keyword`, v0.5.0 design tokens & motion system, v0.6.0 streaming DOM assets, v0.7.0 unified design tokens & Settings modal, v0.8.0 Hermes Agent UI controls, **v0.8.2 Execution Mode Switcher (`#executionModeSwitcher`)** | 9 |
| **Python Total** | | | **78** |

### 3.2 Frontend Markdown & Syntax Test Suite (`node` — 11 Tests)

| Test Item | Focus Area | Tested Invariants |
|---|---|---|
| **Test 1** | URL Sanitization | Verifies `http://`, `https://`, and `mailto:` links are preserved; verifies `javascript:`, `vbscript:`, and `data:` schemes are blocked. |
| **Test 2** | Python Highlighting | Asserts `.tok-keyword` on `def`, `class`, `import`; asserts `.tok-string`, `.tok-comment`, `.tok-function`. |
| **Test 3** | JS/TS Highlighting | Asserts `.tok-keyword` on `const`, `async`, `await`, `function`; asserts `.tok-type` on `Promise`, `string`. |
| **Test 4** | SQL Highlighting | Asserts `.tok-keyword` on `SELECT`, `FROM`, `WHERE`, `JOIN`, `ORDER BY`. |
| **Test 5** | JSON Highlighting | Asserts `.tok-keyword` on JSON keys, `.tok-string` on string values, `.tok-boolean` on `true`. |
| **Test 6** | Bash / Shell Highlighting | Asserts `.tok-keyword` on `if`, `then`, `echo`, `exit`; asserts `.tok-comment` on `#`. |
| **Test 7** | Markdown Links & XSS | Verifies raw HTML `<script>` tags are escaped; verifies safe link `<a>` tag formatting. |
| **Test 8** | Headings & Inline Formatting | Verifies `h1`, `h2`, `h3`, `strong`, `em`, and inline `code` element generation. |
| **Test 9** | GFM Tables | Verifies responsive table wrapper `.msg-table-wrapper`, `.msg-table`, `<th>`, and `<td>`. |
| **Test 10** | Nested Lists | Verifies unordered list nesting and hierarchical indentation without parsing collapse. |
| **Test 11** | Unclosed Code Block Recovery | Verifies dangling/streaming code blocks close cleanly without layout corruption. |
| **Frontend Total** | | **11** |

**Grand Total Automated Tests:** **89 Tests** (78 Python + 11 JavaScript)

---

## 4. Hermes Autonomous Execution & Safety Scenarios Verification

All 10 required operational and security scenarios are verified by dedicated regression tests in `tests/test_hermes.py`:

| Scenario ID | Scenario Description | Expected Behavior | Automated Test | Outcome |
|---|---|---|---|:---:|
| **Scenario 1** | Inspect project | Zero approval dialogs; workspace file tree injected | `test_scenario_1_hermes_inspect_project_autonomous` | **PASS** |
| **Scenario 2** | Create workspace file | Created autonomously; backup created in `.aegis_backups` | `test_scenario_2_hermes_create_file_autonomous` | **PASS** |
| **Scenario 3** | Fix bug in workspace | Fix applied autonomously; file updated on disk | `test_scenario_3_hermes_fix_bug_autonomous` | **PASS** |
| **Scenario 4** | Run test runner | Allowlisted test command executed with exit code and stdout | `test_scenario_4_hermes_run_tests_autonomous` | **PASS** |
| **Scenario 5** | Multi-file modifications | All files modified autonomously in single turn | `test_scenario_5_hermes_multi_file_autonomous` | **PASS** |
| **Scenario 6** | Delete directory or file | High-risk deletion intercepted into human approval queue | `test_scenario_6_hermes_delete_directory_requires_approval` | **PASS** |
| **Scenario 7** | Access outside workspace | Path traversal (`../../etc/passwd`) blocked by security guard | `test_scenario_7_hermes_outside_workspace_blocked` | **PASS** |
| **Scenario 8** | Expose API keys / `.env` | Access to `.env` / credentials blocked and logged to audit | `test_scenario_8_hermes_expose_api_keys_blocked` | **PASS** |
| **Scenario 9** | Switch to Supervised Mode | Patches/commands held in pending approval dialogs | `test_scenario_9_hermes_switch_to_supervised_mode` | **PASS** |
| **Scenario 10** | Native Aegis engine behavior | Native engine retains default supervised approval lifecycle | `test_scenario_10_native_aegis_supervised_by_default` | **PASS** |

---

## 5. Execution Commands

### Run Full Test Verification (Python + Node.js):
```bash
python -m pytest; node tests/test_markdown_renderer.js
```

### Run Python Tests Only:
```bash
python -m pytest
```

### Run Node.js Frontend Renderer Tests:
```bash
node tests/test_markdown_renderer.js
```

---

## 6. Actual Latest Verification Results

### 6.1 Python Test Session (`python -m pytest`)
```
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: E:\Code Tresure\nvidia-nebius-main\nvidia-nebius-main
configfile: pyproject.toml
plugins: anyio-4.14.2, langsmith-0.11.1
collected 78 items

tests\test_approvals.py ..                                               [  2%]
tests\test_audit.py ..                                                   [  5%]
tests\test_chat.py ..........                                            [ 17%]
tests\test_e2e_live.py ....                                              [ 23%]
tests\test_frontend.py .........                                         [ 34%]
tests\test_health.py ..                                                  [ 37%]
tests\test_hermes.py .................                                   [ 58%]
tests\test_llm.py .......                                                [ 67%]
tests\test_memory.py ....                                                [ 73%]
tests\test_projects.py ..                                                [ 75%]
tests\test_provider.py .............                                     [ 92%]
tests\test_workspace.py ......                                           [100%]

============================= 78 passed in 3.98s ==============================
```

### 5.2 Node.js Test Session (`node tests/test_markdown_renderer.js`)
```
--- Running Aegis AI Markdown & Syntax Highlighter Tests ---
✓ Safe URL sanitizer tests passed
✓ Python syntax highlighting tests passed
✓ JavaScript/TypeScript syntax highlighting tests passed
✓ SQL syntax highlighting tests passed
✓ JSON syntax highlighting tests passed
✓ Bash syntax highlighting tests passed
✓ Markdown link rendering and XSS sanitization tests passed
✓ Markdown headings and inline formatting tests passed
✓ Markdown tables tests passed
✓ Nested lists tests passed
✓ Unclosed code block recovery tests passed
ALL 11 JAVASCRIPT MARKDOWN & SYNTAX TESTS PASSED SUCCESFULLY!
```

---

## 6. Security & Design Regression Tests

The test suite includes dedicated regression tests for critical invariants:
1. **Design System & Motion Tokens (`test_frontend.py:test_frontend_obsidian_violet_design_system_and_motion`)**: Validates presence of centralized Obsidian (`#0B0C0F`), Graphite (`#101116`), Platinum (`#E6E4EC`), and Electric Violet (`#A78BFA`) tokens, physics easing (`--ease-out`), keyframes (`heroEntrance`, `chipEntrance`), and SVG suggestion chips.
2. **Unified Design System & Settings Modal (`test_frontend.py:test_frontend_unified_design_system_and_settings`)**: Validates mathematical typography tokens (`--font-size-2xs` to `--font-size-2xl`), spacing scale (`--space-3xs` to `--space-2xl`), shared component foundations (`.status-pill`, `.data-table`, `.empty-state`, `.panel-card`, `.btn-close`), and the complete Settings dialog structure (`#modalSettings`, `#settingsInferenceCard`, `#settingsNetworkCard`, `#settingsSandboxCard`, `#btnRunDiagnostics`).
3. **Hermes Agent UI Controls (`test_frontend.py:test_frontend_hermes_agent_controls`)**: Validates `#agentModeSwitcher`, `#btnBackendAegis`, `#btnBackendHermes`, and `#settingsHermesCard` existence, attributes, and styling in the DOM.
4. **Hermes Subprocess Sandboxing & Anti-Fallback Invariant (`test_hermes.py:test_hermes_anti_fallback_on_ollama_failure`)**: Verifies that Hermes subprocess execution is locked to `--in <workspace_path>`, disables unmonitored tools (`--toolsets ""`), and strictly returns 503/502 on local Ollama timeout without silent cloud failover.
5. **Anti-Fallback Invariant (`test_provider.py:test_anti_fallback_invariant`)**: Confirms that when `LLM_PROVIDER=ollama`, an Ollama timeout or connection error returns an explicit connection error and never dispatches to cloud endpoints.
6. **Path Traversal Rejection (`test_workspace.py:test_path_traversal_blocked`)**: Attempts to read `../../etc/passwd` or `..\\Windows\\win.ini` outside `./workspace` result in an immediate `PermissionError`.
7. **Command Allowlist Enforcement (`test_approvals.py:test_disallowed_command`)**: Commands outside `pytest`, `python -m unittest`, and `npm test` are rejected during approval execution.
8. **Secret Shield (`test_memory.py:test_secret_redaction`)**: Passwords, API tokens, and private keys submitted via prompts are scrubbed before storage in SQLite.
9. **XSS & Protocol Hijack Blocking (`test_markdown_renderer.js`)**: Injected `<script>` tags and `javascript:` URIs are neutralized during Markdown sanitization.
10. **Native SSE Token Streaming & Abort Resilience (`test_chat.py:test_chat_stream_tokens_and_completion_event`)**: Validates that chunked token events and completion metadata arrive in standard SSE format, that mid-stream proposals are parsed cleanly, and that client abort triggers immediate backend generator cleanup without corrupting history.

