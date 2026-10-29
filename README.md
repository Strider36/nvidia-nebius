# Aegis AI — Private Personal AI Operator

[![Version](https://img.shields.io/badge/version-0.8.1-A78BFA.svg)](pyproject.toml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](pyproject.toml)
[![Tests](https://img.shields.io/badge/tests-80%20passed%20(100%25)-brightgreen.svg)](TESTING.md)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)
[![Theme](https://img.shields.io/badge/design-Unified%20Obsidian%20%26%20Electric%20Violet-101116.svg)](frontend/styles.css)

**Aegis AI** is a functional, privacy-first personal AI assistant and autonomous coding operator featuring **Dual-Provider Inference** and **Pluggable Agent Backends**:
1. **Local Inference**: Powered by **NVIDIA Nemotron 3.5 Bolt E4B** running locally on your hardware via **Ollama** (`http://127.0.0.1:11434`).
2. **Cloud Inference**: Powered by **NVIDIA Nemotron** via **Nebius Token Factory** or **OpenRouter** (`https://openrouter.ai/api/v1`).
3. **Pluggable Agent Backends**: Choose seamlessly between **Native Aegis** reasoning engine and **Hermes Agent** backend CLI (`v0.22.5`).

It combines a **Unified Obsidian & Electric Violet Design System** across all 7 views with **native SSE token streaming**, an optional **Hermes Agent backend**, a zero-dependency multi-language syntax highlighter, resilient Markdown rendering, client-side request cancellation, persistent semantic memory in SQLite, structured project/task organization, reusable developer skills, and a restricted workspace sandbox requiring **human-in-the-loop approval** before any code patch or allowlisted test runner is executed.

---

## Key Capabilities

- **Pluggable Agent Backends (Native Aegis + Hermes Agent)**: Seamlessly toggle between **Native Aegis** reasoning engine and the **Hermes Agent CLI** (`v0.22.5`). Hermes operates via a narrow subprocess invocation protocol (`hermes chat --query-file ... --format stream-json --oneshot`) backed directly by your local NVIDIA Nemotron Ollama instance or configured Cloud provider.
- **Strict Hermes Subprocess Sandboxing & Human Approval Enforcement**: Hermes process execution is constrained strictly to `./workspace` (`--in <workspace_path>`) with external tools disabled (`--toolsets ""`). File modifications and command actions emitted by Hermes (`<<<PROPOSE_PATCH>>>`, `<<<PROPOSE_COMMAND>>>`) are intercepted by Aegis's supervisor and placed into the SQLite pending approvals queue—preventing arbitrary shell access or unattended filesystem writes.
- **Unified Premium Design System (Across All 7 Views)**: A single cohesive design language applied uniformly to **Main Chat, Skills, Memory, Approvals, Workspace, Audit, and Settings**. Features mathematical typography tokens (`--font-size-2xs` to `--font-size-2xl`), standardized spacing scales (`--space-3xs` to `--space-2xl`), hairline borders (`#292B32`), accessible 28x28px geometric SVG close buttons (`aria-label="Close modal"`), and clean, flat surfaces eliminating gratuitous card-in-card nesting.
- **Dedicated Settings & Provider Diagnostics View**: Comprehensive `#modalSettings` dialog inspecting configured provider, local vs cloud models, loopback interfaces (`127.0.0.1:8000`), SQLite engine status, sandbox boundaries, Hermes Agent diagnostics, and one-click connectivity diagnostics (`#btnRunDiagnostics`).
- **Native Server-Sent Events (SSE) Token Streaming**: Real-time token streaming from local Ollama (`stream: true`), cloud models (`stream=True`), and Hermes streaming JSONL events through `POST /api/chat/stream`. Features client-side chunk decoding via `ReadableStream`, a realistic blinking streaming cursor (`.streaming-cursor`), intelligent auto-scroll locking, active stream cancellation via `#btnStop` and `Escape`, and automatic fallback protection.
- **Obsidian & Electric Violet Design Identity**: A bespoke software developer identity built on Obsidian canvas (`#0B0C0F`), Graphite sidebar (`#101116`), elevated surfaces (`#15171D`, `#1B1D25`), Platinum text (`#E6E4EC`), and Electric Violet accents (`#A78BFA`). Features high-contrast WCAG-compliant typography and refined status pills (`.status-pill`).
- **Physics-Based Motion System**: Fluid, restrained interaction system governed by centralized physics tokens (`--ease-out`, `--duration-fast/normal/slow`). Includes smooth fade-and-rise hero entrance, staggered suggestion chip animations (`60ms`, `110ms`, `160ms`, `210ms`), micro-interaction press scaling (`scale(0.98)`), active navigation indicators, and full `@media (prefers-reduced-motion: reduce)` support.
- **Pure Geometric SVG Iconography**: Zero platform-dependent emojis. Every interface action, suggestion chip, memory badge, file list item, and approval tag uses crisp, bespoke inline SVGs with uniform stroke geometry.
- **Multi-Language Syntax Highlighting Engine**: Zero-dependency lexical tokenizer supporting **Python, JavaScript, TypeScript, Java, SQL, JSON, Bash, PowerShell, HTML/XML, CSS, YAML, and Markdown**. Monospace code canvases include detected language badges, copy code buttons, dark syntax tokens, and horizontal scrolling for long lines.
- **Robust Markdown & Safe Sanitization**: Full support for headings, blockquotes, arbitrary nested lists, inline formatting (`**bold**`, `*italic*`, `` `code` ``), and responsive GitHub Flavored Markdown tables with horizontal overflow wrappers. Malformed HTML is escaped and URLs are sanitized strictly allowing `http(s)://` and `mailto:` while blocking `javascript:` and `data:` schemes.
- **Assistant Message Actions & Toast Notifications**: One-click **Copy response** and individual **Copy code** buttons with visual checkmark states and animated toast alerts. Automatic fallback to legacy clipboard mechanisms (`document.execCommand`) ensures reliable copying across all browser security contexts.
- **Real Request Cancellation (`AbortController`)**: Interactive stop button (`#btnStop`) and `Escape` key trigger true client-side cancellation, immediately halting in-flight HTTP requests and restoring composer controls without corrupting conversation history.
- **Dual-Provider Architecture with Zero Silent Fallback**: Seamlessly toggle between local zero-data-leakage Ollama inference (NVIDIA Nemotron 3.5 Bolt E4B) and high-throughput cloud inference directly from the UI or API at runtime without restarting the server. A local failure will **never** silently route private code to the cloud.
- **Persistent Local Memory**: Stores developer preferences, project context, instructions, and session summaries in SQLite. Keyword-indexed retrieval automatically matches relevant memories per prompt. Sensitive data (passwords, tokens, keys) is blocked at the memory gateway.
- **Safe Coding Workspace**: Restricted to `./workspace` (or configured `AEGIS_WORKSPACE`). Enforces path canonicalization, blocks path traversal (`../`), forbids access to `.env` or SSH keys, computes unified diffs, detects concurrent file change conflicts, and automatically creates timestamped backups in `.aegis_backups/` before applying modifications.
- **Human Approval Lifecycle**: Consequential actions transition through `PROPOSED -> PENDING_APPROVAL -> APPROVED -> EXECUTING -> SUCCEEDED / FAILED`. The model cannot self-approve; every patch, task addition, and allowlisted test runner command requires explicit user confirmation with full diffs and risk disclosure.
- **Allowlisted Command Execution**: Prohibits arbitrary shell access. Only explicitly allowlisted test runner commands (`pytest`, `python -m unittest`, `npm test`) can be executed with strict timeouts and isolated process spawning.
- **Reusable Developer Skills**: Built-in system skills with explicit tool bindings (Project Planner, Code Explainer, Debugger, Test Writer).
- **Full Audit Trail**: Every sensitive operation, approval decision, and execution result is logged to SQLite with automatic secret sanitization in a high-density `.data-table` with sticky headers.

---

## Architecture Diagram

```
+-------------------------------------------------------------------------------------------------+
|                                           LOCAL HOST                                            |
|                                                                                                 |
|  +------------------------+                           +--------------------------------------+  |
|  | Obsidian/Violet UI     | <-----------------------> | FastAPI Backend (127.0.0.1:8000)     |  |
|  | - Local/Cloud Toggle   |                           +------------------+-------------------+  |
|  | - Native/Hermes Toggle |                                              |                      |
|  | - SSE Streaming Client |                                              v                      |
|  +------------------------+                           +--------------------------------------+  |
|                                                       | Agent Routing & Security Supervisor  |  |
|                                                       | - Per-Request Provider Snap          |  |
|                                                       | - Anti-Fallback Invariant            |  |
|                                                       | - Human Approval Interceptor         |  |
|                                                       | - Workspace Path Guard               |  |
|                                                       +----------+-------------------+-------+  |
|                                                                  |                   |          |
|                                          +-----------------------+                   |          |
|                                          v                                           v          |
|                        +------------------------------------+      +-------------------------+  |
|                        | Native Aegis Engine (LLMService)   |      | Hermes Subprocess Adapter| |
|                        | - System Prompt Composition        |      | (HermesService)         |  |
|                        | - SSE Generator                    |      | - CLI: hermes.exe chat  |  |
|                        | - Direct Model API                 |      | - --in ./workspace      |  |
|                        +-----------------+------------------+      | - --toolsets ""         |  |
|                                          |                         | - JSONL Stream Decoder  |  |
|                                          |                         +------------+------------+  |
|                                          +-----------------+--------------------+               |
|                                                            |                                    |
|                       +------------------------------------+--------------------------------+   |
|                       |                                    |                                |   |
|                       v                                    v                                v   |
|              +-----------------+                  +-----------------+              +-----------------+
|              | SQLite Database |                  | Reusable Skills |              | Safe Workspace  |
|              | - Memories      |                  | - Planner       |              | (./workspace)   |
|              | - Projects      |                  | - Explainer     |              | - Unified Diffs |
|              | - Approvals     |                  | - Debugger      |              | - Auto-Backups  |
|              | - Audit Trail   |                  | - Test Writer   |              +-----------------+
|              +-----------------+                  +-----------------+                                 |
+-----------------------|---------------------------------------------------------------------|---+
                        | HTTP (Localhost)                                                    | HTTPS
                        v                                                                     v
          +-------------------------------+                                 +-----------------------------------+
          |       Ollama Local Daemon     |                                 |    Nebius Token Factory Cloud     |
          |     (http://127.0.0.1:11434)  |                                 |     OpenRouter API Gateway        |
          |  NVIDIA Nemotron 3.5 Bolt E4B |                                 |    NVIDIA Nemotron Inference      |
          +-------------------------------+                                 +-----------------------------------+
```

---

## Prerequisites (Windows 11)

- **Operating System**: Windows 11 (or Windows 10 build 19041+), Linux, or macOS.
- **Python**: Python 3.11+ (Python 3.11, 3.12, 3.13, 3.14 verified).
- **Node.js**: Node.js v18.0.0+ (verified on v24.19.0) for running the client-side test suite (zero `npm` dependencies required).
- **Hardware (for Local Ollama)**:
  - Recommended: NVIDIA GeForce RTX 3060+ (8 GB+ VRAM) or RTX 40-series GPU.
  - Supported: 16 GB+ system RAM for CPU offloading.

---

## Installation & Setup

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/Strider36/nvidia-nebius.git aegis-ai
cd aegis-ai

# Create virtual environment
python -m venv venv

# Activate on Windows:
venv\Scripts\activate
# Activate on Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Local Model Setup (Ollama with NVIDIA Nemotron 3.5 Bolt E4B)
To run local private inference:
1. Download and install **Ollama for Windows** from [ollama.com](https://ollama.com).
2. Pull the NVIDIA Nemotron 3.5 Bolt model:
   ```bash
   ollama pull nemotron-3.5-bolt:e4b
   ```
3. Verify that the model is present:
   ```bash
   ollama list
   ```
   *Expected output lists `nemotron-3.5-bolt:e4b`.*
4. Ensure the Ollama daemon is running (`http://127.0.0.1:11434`).

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` to configure your preferred settings:
```ini
# Inference Provider Selection ('ollama' or 'cloud')
LLM_PROVIDER=ollama

# Local Ollama Inference Configuration
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=nemotron-3.5-bolt:e4b
OLLAMA_TIMEOUT=60.0

# Cloud Inference Configuration (Optional if using Local Ollama)
OPENROUTER_API_KEY=your_openrouter_api_key_here
NEBIUS_BASE_URL=https://openrouter.ai/api/v1
NEBIUS_MODEL_ID=nvidia/nemotron-3-nano-30b-a3b

# Hermes Agent Configuration (Optional Backend)
HERMES_ENABLED=true
HERMES_BIN_PATH=C:\Users\jayan\AppData\Local\hermes\bin\hermes.exe
HERMES_TIMEOUT=120.0
DEFAULT_AGENT_BACKEND=aegis

# Aegis Workspace & Database Settings
AEGIS_WORKSPACE=./workspace
AEGIS_DATABASE_PATH=./aegis.db
AEGIS_HOST=127.0.0.1
AEGIS_PORT=8000
AEGIS_DEBUG=false
```

---

## Running the Application

Start the Aegis AI server:
```bash
python main.py
```
Or directly with uvicorn:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## Dual-Provider & Agent Backend Switching

Aegis AI lets you switch both the inference provider and the agent reasoning backend **without restarting the server**:

1. **Inference Provider (Local / Cloud)**:
   - In the top header bar, click **Local** or **Cloud**.
   - The indicator dot reflects immediate connectivity (green for ready, amber for unconfigured, red for offline).
   - The active model tag updates dynamically.
   - REST API: `GET /api/provider`, `POST /api/provider` with `{"provider": "ollama"}` or `{"provider": "cloud"}`.

2. **Agent Reasoning Backend (Native Aegis / Hermes Agent)**:
   - In the top header bar, toggle between **Native Aegis** and **Hermes Agent**.
   - **Native Aegis**: Uses Aegis's internal prompt synthesis and tool-calling engine.
   - **Hermes Agent**: Wraps the local Hermes CLI (`hermes.exe chat`) sandboxed inside `./workspace` with external autonomous tools disabled (`--toolsets ""`).
   - Consequential file modifications (`<<<PROPOSE_PATCH>>>`) and test commands (`<<<PROPOSE_COMMAND>>>`) emitted by Hermes are caught by Aegis's supervisor and placed into the SQLite human approval queue.
   - Diagnostic status: `GET /api/hermes/status` inspects binary detection, version, and active provider readiness.

---

## Running Automated Tests

All tests execute deterministically and require **zero API credits**.

### Run Full Verification (Python + Node.js — 80 Tests):
```bash
python -m pytest; node tests/test_markdown_renderer.js
```

### Run Python Backend Tests:
```bash
python -m pytest
```

### Run Node.js Frontend Renderer Tests:
```bash
node tests/test_markdown_renderer.js
```

Expected output:
```
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
collected 69 items
tests\test_approvals.py ..                                               [  2%]
tests\test_audit.py ..                                                   [  5%]
tests\test_chat.py ..........                                            [ 20%]
tests\test_e2e_live.py ....                                              [ 26%]
tests\test_frontend.py .........                                         [ 39%]
tests\test_health.py ..                                                  [ 42%]
tests\test_hermes.py ........                                            [ 53%]
tests\test_llm.py .......                                                [ 63%]
tests\test_memory.py ....                                                [ 69%]
tests\test_projects.py ..                                                [ 72%]
tests\test_provider.py .............                                     [ 91%]
tests\test_workspace.py ......                                           [100%]
============================= 69 passed in 3.77s ==============================

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

## Common Errors & Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| `Unable to reach Ollama at http://127.0.0.1:11434` | Ollama daemon is not running | Start Ollama from Start Menu or run `ollama serve` in a terminal. |
| `Model 'nemotron-3.5-bolt:e4b' not found in Ollama` | The model has not been downloaded | Run `ollama pull nemotron-3.5-bolt:e4b`. |
| Inference timeout after 60s | First-time model loading onto CPU/VRAM | Set `OLLAMA_TIMEOUT=120.0` in `.env` to accommodate slower CPU offloading. |
| Port 8000 already in use | Another application or previous Aegis instance is running | Run on alternate port: `python main.py --port 8001` or kill existing process. |
| Clipboard copy toast displays error | Browser permissions restricted (non-HTTPS or iframe) | Aegis automatically uses `document.execCommand('copy')` fallback; ensure the window is focused. |
| Markdown tables broken | Text missing trailing pipe or newline | Aegis table parser formats GFM tables; ensure standard Markdown table syntax. |

---

## Security Model & Privacy Limitations

1. **Strict Data Sovereignty**: When `LLM_PROVIDER=ollama`, prompts and code are processed 100% on localhost. Aegis includes an architectural anti-fallback invariant that prevents silent rerouting to cloud endpoints.
2. **Subprocess Whitelist**: Shell execution is strictly restricted to allowlisted test runners (`pytest`, `python -m unittest`, `npm test`). Arbitrary shell execution (`rm`, `sh`, `curl`, `powershell`) is blocked.
3. **Workspace Boundary**: All file operations resolve strictly inside `AEGIS_WORKSPACE` (`./workspace`). Traversal attempts (`../`) and sensitive patterns (`.env`, `.git`, `*.pem`, `id_rsa`) are rejected.
4. **Pre-Modification Rollback**: Every approved patch creates an automatic timestamped backup in `.aegis_backups/` before files are touched.
5. **Single-User Local Trust**: Designed for an individual developer running on `127.0.0.1`. It does not include multi-tenant user authentication or external network ingress hardening.
