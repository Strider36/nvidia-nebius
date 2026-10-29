# Aegis AI — Private Personal AI Operator

**Aegis AI** is a functional, security-first personal AI assistant and autonomous coding operator powered by **NVIDIA Nemotron** running through **Nebius Token Factory**.

It combines a polished obsidian-themed responsive web interface, persistent semantic memory in SQLite, structured project/task organization, reusable developer skills, and a restricted workspace sandbox requiring **human-in-the-loop approval** before consequential modifications or test executions are made.

---

## Key Capabilities

- **Hybrid Privacy Architecture**: All memory, task backlogs, audit logs, and workspace files remain strictly local on your PC. Cloud inference is used solely for bounded prompt generation through Nebius Token Factory.
- **Persistent Local Memory**: Stores developer preferences, project context, instructions, and session summaries in SQLite. Keyword-indexed retrieval automatically retrieves relevant memories per prompt and displays them transparently in the UI. Sensitive data (passwords, tokens, keys) is blocked at the memory gateway.
- **Safe Coding Workspace**: Restricted to `./workspace` (or your configured `AEGIS_WORKSPACE`). Enforces path canonicalization, blocks path traversal (`../`), forbids access to `.env` or SSH keys, computes unified diffs, detects concurrent file change conflicts, and automatically creates timestamped backups in `.aegis_backups/` before applying modifications.
- **Human Approval Lifecycle**: Consequential actions transition through `PROPOSED -> PENDING_APPROVAL -> APPROVED -> EXECUTING -> SUCCEEDED / FAILED`. The model cannot self-approve; every patch, task addition, and allowlisted command requires explicit user confirmation with full diffs and risk disclosure.
- **Allowlisted Command Execution**: Prohibits arbitrary shell access. Only explicitly allowlisted test runner commands (`pytest`, `python -m unittest`, `npm test`) can be executed with strict timeouts and isolated process spawning.
- **Reusable Skills**: Comes with 4 built-in system skills with explicit tool bindings:
  1. **Project Planner**: Deconstructs goals into milestones and structured tasks.
  2. **Code Explainer**: Inspects code structure, edge cases, and architectural tradeoffs.
  3. **Debugger**: Diagnoses stack traces and formulates minimal, reviewable patches.
  4. **Test Writer**: Generates comprehensive unit tests and executes test runners.
- **Full Audit Trail**: Every sensitive operation, approval decision, and execution result is logged to SQLite with automatic secret sanitization.

---

## Architecture Diagram

```
+-------------------------------------------------------------------------+
|                              LOCAL HOST                                 |
|                                                                         |
|  +------------------------+          +-------------------------------+  |
|  | Modern Web UI (Dark)   | <------> | FastAPI Backend (127.0.0.1)   |  |
|  | HTML / CSS / VanillaJS |          +---------------+---------------+  |
|  +------------------------+                          |                  |
|                                                      v                  |
|  +-------------------------------------------------------------------+  |
|  | Aegis Security & Orchestration Layer                              |  |
|  | - Path Resolution & Traversal Guard                               |  |
|  | - Human Approval Life Cycle Engine                                |  |
|  | - Command Allowlist Verifier (pytest, unittest, npm)              |  |
|  | - Sensitive Token Redactor & Secret Shield                        |  |
|  +-----------+----------------------+--------------------+-----------+  |
|              |                      |                    |              |
|              v                      v                    v              |
|     +-----------------+    +-----------------+  +-----------------+     |
|     | SQLite Database |    | Safe Workspace  |  | Reusable Skills |     |
|     | - Memories      |    | (./workspace)   |  | - Planner       |     |
|     | - Projects      |    | - Diffs & Files |  | - Explainer     |     |
|     | - Approvals     |    | - Auto-Backups  |  | - Debugger      |     |
|     | - Audit Trail   |    |                 |  | - Test Writer   |     |
|     +-----------------+    +-----------------+  +-----------------+     |
+--------------------------------------|----------------------------------+
                                       | HTTPS (Bounded Tokens)
                                       v
                     +-----------------------------------+
                     |   Nebius Token Factory Cloud      |
                     |   NVIDIA Nemotron Inference       |
                     +-----------------------------------+
```

---

## Installation & Setup

### 1. Prerequisites
- **Python**: Python 3.11+ (Python 3.11, 3.12, 3.13, 3.14 supported).
- **OS**: Windows 11, Linux, or macOS.

### 2. Clone and Setup Environment
```bash
git clone <repository_url> aegis-ai
cd aegis-ai

# Optional: Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Open `.env` and set your credentials (OpenRouter or Nebius Token Factory):
```ini
# OpenRouter / Nebius Model Inference Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
NEBIUS_BASE_URL=https://openrouter.ai/api/v1
NEBIUS_MODEL_ID=nvidia/nemotron-3-nano-30b-a3b

# Aegis Workspace & Database Settings
AEGIS_WORKSPACE=./workspace
AEGIS_DATABASE_PATH=./aegis.db
AEGIS_HOST=127.0.0.1
AEGIS_PORT=8000
AEGIS_DEBUG=false
```

*Note: If `NEBIUS_API_KEY` is omitted, the application starts gracefully in a degraded mode, allowing full access to the UI, persistent memories, projects, workspace explorer, and approvals.*

---

## Launching the Application

Start the Aegis AI server:
```bash
python main.py
```
Or with uvicorn directly:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## Building and Distribution

Aegis AI supports multiple production-ready build targets:

### 1. Build Standard Wheel & Source Package (PEP 517)
```bash
python scripts/build.py --package
```
This produces ready-to-distribute packages in `dist/`:
- `dist/aegis_ai-0.1.0-py3-none-any.whl`
- `dist/aegis_ai-0.1.0.tar.gz`

Install globally into any environment:
```bash
pip install dist/aegis_ai-0.1.0-py3-none-any.whl
# Launch from anywhere via the generated CLI command:
aegis-ai
```

### 2. Standalone Portable Binary (PyInstaller)
Bundle the Python interpreter, FastAPI, SQLite, frontend assets, and skill definitions into a standalone build:
```bash
python scripts/build.py --standalone
```
The output directory `dist/aegis-ai/` contains the self-contained executable.

### 3. Containerized Build (Docker & Docker Compose)
Build and run Aegis AI in an isolated container:
```bash
docker compose up --build -d
```
Access the application at `http://127.0.0.1:8000`.

### 4. Build Automation Utility (`scripts/build.py`)
Run all verification, package, and cleanup commands:
```bash
# Clean, run test suite, and build distribution package
python scripts/build.py --test --package

# Full end-to-end build (clean, test, wheel, standalone binary)
python scripts/build.py --all
```

---

## Performance Optimizations

1. **High-Performance SQLite Engine**:
   - `PRAGMA journal_mode = WAL`: High concurrency reader-writer execution.
   - `PRAGMA synchronous = NORMAL`: Skips redundant fsyncs while ensuring zero database corruption risk.
   - `PRAGMA cache_size = -64000`: 64 MB in-memory page cache for lightning queries.
   - `PRAGMA mmap_size = 268435456`: 256 MB memory-mapped I/O.
2. **ASGI & Network Optimizations**:
   - `GZipMiddleware`: Compresses static files and JSON responses over 1 KB, reducing transfer size by up to 70%.
   - **Static Asset Caching**: 1-hour cache-control policy for static styles, scripts, and logos.
   - **Security Headers Middleware**: Enforces `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1`, and `Referrer-Policy: strict-origin-when-cross-origin`.
3. **Frontend UX Optimizations**:
   - Keyboard ergonomics: Press `Enter` to submit, `Shift+Enter` for multiline text.
   - Auto-expanding message textarea up to 160px.
   - Live pulsating thinking indicator with dynamic reasoning status stages.
   - Real-time button spinners for async operations.

---

## Running Automated Tests

All tests mock external inference and require **zero API credits** to execute.

Run the complete test suite:
```bash
python -m pytest
```

Expected output:
```
============================= test session starts =============================
collected 28 items

tests/test_approvals.py ..                                               [  7%]
tests/test_audit.py ..                                                   [ 14%]
tests/test_chat.py ....                                                  [ 28%]
tests/test_frontend.py ..                                                [ 35%]
tests/test_health.py ..                                                  [ 42%]
tests/test_llm.py ....                                                   [ 57%]
tests/test_memory.py ....                                                [ 71%]
tests/test_projects.py ..                                                [ 78%]
tests/test_workspace.py ......                                           [100%]

============================= 28 passed in 1.62s ==============================
```

---

## Verification & Hackathon Demo Script

Follow this repeatable 5-minute walkthrough to demonstrate Aegis AI:

### Step 1: Health & System Status Check
1. Open `http://127.0.0.1:8000`.
2. Observe the top-left status pill:
   - Green indicator: Nebius Token Factory is connected.
   - Model name displayed in sidebar footer (`Nemotron-70B`).
   - Server bound to `127.0.0.1`.

### Step 2: Persistent Semantic Memory
1. In the sidebar, click the **Memory** tab.
2. Click **+ New Memory**.
3. Select **Preference** and enter:
   `"Always generate Python code with strict type annotations and docstrings."`
4. Click **Save Memory**.
5. Refresh the browser or restart the server: notice the memory remains permanently stored in SQLite.

### Step 3: Project & Task Backlog
1. Click the **Active Project** dropdown or folder icon.
2. Click **+ Add Project**, name it `"Microservices MVP"`, and create it.
3. Add a task: `"Implement JWT verification middleware"`.

### Step 4: Reusable Skills in Action
1. Return to the chat session.
2. Select the **Test Writer** skill pill from the bottom bar.
3. Send: `"Propose a new test file test_math.py with tests for a factorial function."`
4. Notice how Aegis AI retrieves the memory: `🧠 Memories Applied: [preference] Always generate Python code with strict type annotations...`
5. The assistant outputs the solution and presents a **Human Approval Card** with the proposed diff and risk disclosure.

### Step 5: Safe Workspace & Human Approval Execution
1. Inspect the **Approval Card**: notice the unified diff and reason.
2. Click **✓ Approve & Apply**.
3. Open the **Workspace** tab: verify `test_math.py` has been written to `./workspace/test_math.py`.
4. Propose running the tests: click **Run Allowlisted Tests** and enter `pytest`.
5. Approve the test execution in the **Approvals** tab and observe the exit status and stdout.

### Step 6: Security Audit Trail
1. Open the **Audit** tab.
2. View the complete, chronologically ordered log of proposals, user approvals, execution statuses, and sanitized inputs.

---

## Security Model & Known Limitations

- **Single Trusted Local User**: Aegis AI MVP is designed to run locally on `127.0.0.1` for an individual developer. It does not provide multi-tenant authentication or public-facing role-based access control.
- **Subprocess Isolation**: Commands are strictly restricted to the allowlist (`pytest`, `python -m pytest`, `python -m unittest`, `npm test`, `node --test`). Arbitrary shell execution (`sh`, `bash`, `cmd`, `powershell`) is blocked.
- **Path Confinement**: All file read/write operations must resolve strictly within `AEGIS_WORKSPACE`. Traversal sequences (`../`) and sensitive patterns (`.env`, `*.pem`, `*.key`, `id_rsa`) are rejected with `WorkspaceSecurityError`.
- **Zero Silent Overwrites**: Patches are rejected if the file on disk was modified after the diff was generated. Automated timestamped backups are preserved in `.aegis_backups/`.

