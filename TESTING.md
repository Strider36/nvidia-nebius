# Aegis AI — Comprehensive Testing Guide & Verification Suite

**Version:** 0.4.0  
**Last Updated:** 2026-10-29  
**Status:** 100% Passing (56/56 Automated Tests)  

---

## 1. Testing Strategy & Principles

All unit, integration, and security tests in Aegis AI adhere to five strict testing principles:
1. **Deterministic & Offline**: Tests execute without internet access. Cloud endpoints are mocked via OpenAI client fixtures, and local Ollama calls are mocked via `httpx` transport fixtures.
2. **Persistent DB Isolation**: Each test run uses an isolated in-memory or temporary throwaway SQLite database (`tempfile.TemporaryDirectory`) ensuring zero state leakage between tests.
3. **Dual-Stack Verification**: Tests validate both the Python backend application (via `pytest` and `fastapi.testclient.TestClient`) and the client-side JavaScript rendering engine (via Node.js `node:vm` harness).
4. **Anti-Fallback & Security Invariant Checks**: Automated assertions verify that local inference failures never trigger silent cloud fallbacks, path traversal attempts are rejected, and secrets are redacted from logs.
5. **Human Approval Enforcement**: Tests confirm that file modifications and command executions cannot occur autonomously.

---

## 2. Test Environment Requirements

- **Operating System**: Windows 11, Linux (Ubuntu 22.04+), or macOS (Sonoma+).
- **Python Runtime**: Python 3.11, 3.12, 3.13, or 3.14.
- **Node.js Runtime**: Node.js v18.0.0+ (verified on v24.19.0) with zero external `npm` dependencies (uses native `node:assert` and `node:vm`).

### Install Test Dependencies
```bash
pip install -r requirements.txt
```
*(No `npm install` is required; frontend tests use native Node.js core libraries).*

---

## 3. Test Suites & Coverage Breakdown

### 3.1 Python Backend Test Suite (`pytest` — 45 Tests)

| Test Module | Focus Area | Tested Invariants | Test Count |
|---|---|---|:---:|
| [`tests/test_provider.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_provider.py) | Dual-Provider Inference | Ollama HTTP payload, 404 model missing, timeouts, connection errors, runtime switching, per-request isolation, anti-fallback invariant | 12 |
| [`tests/test_llm.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_llm.py) | Cloud Provider Client | OpenAI SDK compatibility, authentication errors, quota limits, unconfigured fallback | 4 |
| [`tests/test_chat.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_chat.py) | Chat Orchestration | Session history, memory context injection, proposal parsing (`<<<PROPOSE_PATCH>>>`, `<<<PROPOSE_COMMAND>>>`, `<<<PROPOSE_TASK>>>`), conversation rename endpoint | 6 |
| [`tests/test_approvals.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_approvals.py) | Approval Lifecycle | State machine transitions (`PROPOSED -> PENDING_APPROVAL -> APPROVED -> EXECUTING -> SUCCEEDED / REJECTED`), execution safety | 2 |
| [`tests/test_workspace.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_workspace.py) | Workspace Sandboxing | Path canonicalization, traversal blocking (`../`), unified diff computation, timestamped pre-modification backups | 6 |
| [`tests/test_memory.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_memory.py) | Persistent SQLite Memory | Memory CRUD, keyword index retrieval, secret shield blocking credentials at gateway | 4 |
| [`tests/test_projects.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_projects.py) | Projects & Backlog | Project creation, milestone task tracking, status updates | 2 |
| [`tests/test_health.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_health.py) | Health & Readiness | Health probe payload, non-blocking DB and provider connectivity, secret non-leakage | 2 |
| [`tests/test_audit.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_audit.py) | Audit Trail Persistence | Audit logging to SQLite, automatic secret token scrubbing in logs | 2 |
| [`tests/test_frontend.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_frontend.py) | Static Assets & UI | Asset serving (`index.html`, `styles.css`, `app.js`), suggestion chips, `#btnStop`, `#toastContainer`, `highlightSyntax`, `.tok-keyword` | 5 |
| **Python Total** | | | **45** |

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

**Grand Total Automated Tests:** **56 Tests** (45 Python + 11 JavaScript)

---

## 4. Execution Commands

### Run Full Test Verification (Python + Node.js):
```bash
python -m pytest && node tests/test_markdown_renderer.js
```

### Run Python Tests Only:
```bash
python -m pytest
```

### Run Python Tests Verbose:
```bash
python -m pytest -v
```

### Run Specific Test Modules:
```bash
# Provider and isolation tests
python -m pytest tests/test_provider.py -v

# Frontend integration tests
python -m pytest tests/test_frontend.py -v

# Workspace security and sandboxing tests
python -m pytest tests/test_workspace.py -v
```

### Run Node.js Frontend Renderer Tests:
```bash
node tests/test_markdown_renderer.js
```

---

## 5. Actual Latest Verification Results

### 5.1 Python Test Session (`python -m pytest`)
```
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: E:\Code Tresure\nvidia-nebius-main\nvidia-nebius-main
configfile: pyproject.toml
plugins: anyio-4.14.2, langsmith-0.11.1
collected 45 items

tests\test_approvals.py ..                                               [  4%]
tests\test_audit.py ..                                                   [  8%]
tests\test_chat.py ......                                                [ 22%]
tests\test_frontend.py .....                                             [ 33%]
tests\test_health.py ..                                                  [ 37%]
tests\test_llm.py ....                                                   [ 46%]
tests\test_memory.py ....                                                [ 55%]
tests\test_projects.py ..                                                [ 60%]
tests\test_provider.py ............                                      [ 86%]
tests\test_workspace.py ......                                           [100%]

============================= 45 passed in 3.06s ==============================
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

## 6. Security Regression Tests

The test suite includes dedicated regression tests for critical security invariants:
1. **Anti-Fallback Invariant (`test_provider.py:test_anti_fallback_invariant`)**: Confirms that when `LLM_PROVIDER=ollama`, an Ollama timeout or connection error returns an explicit connection error and never dispatches to cloud endpoints.
2. **Path Traversal Rejection (`test_workspace.py:test_path_traversal_blocked`)**: Attempts to read `../../etc/passwd` or `..\\Windows\\win.ini` outside `./workspace` result in an immediate `PermissionError`.
3. **Command Allowlist Enforcement (`test_approvals.py:test_disallowed_command`)**: Commands outside `pytest`, `python -m unittest`, and `npm test` are rejected during approval execution.
4. **Secret Shield (`test_memory.py:test_secret_redaction`)**: Passwords, API tokens, and private keys submitted via prompts are scrubbed before storage in SQLite.
5. **XSS & Protocol Hijack Blocking (`test_markdown_renderer.js`)**: Injected `<script>` tags and `javascript:` URIs are neutralized during Markdown sanitization.

---

## 7. Known Limitations & Untested Areas

- **Native SSE Token Streaming**: Incremental Server-Sent Events streaming is scheduled for Milestone 5 (v0.5.0); current chat communication uses complete request-response payloads with client-side cancellation.
- **Physical GPU Load Tests**: Automated tests mock inference HTTP responses for speed and determinism; testing inference speeds of local Nemotron under sustained 100+ concurrent GPU requests requires live NVIDIA hardware benchmarking.
