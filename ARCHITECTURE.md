# Aegis AI — Architectural Design Document

## 1. Executive Summary

Aegis AI is an obsidian-themed, privacy-first personal AI operator built around a **dual-provider inference architecture**:
1. **Local Provider**: Direct interaction with the **Ollama HTTP API** running locally on `http://127.0.0.1:11434` with the **NVIDIA Nemotron 3.5 Bolt E4B** model.
2. **Cloud Provider**: OpenAI-compatible API interaction with **Nebius Token Factory** or **OpenRouter** (`https://openrouter.ai/api/v1`) using the NVIDIA Nemotron model family.

The core design principle is **strict isolation and zero silent fallback**: local queries never leave the developer machine on failure, and all consequential actions (file patches, commands, tasks) require explicit human approval regardless of the provider used.

---

## 2. Component Architecture

```
+---------------------------------------------------------------------------------------+
|                                    BROWSER UI                                         |
|  - Obsidian Dark Theme                                                                |
|  - Topbar Provider Switcher [Local (Ollama) | Cloud]                                  |
|  - Realtime Provider Connectivity Dot & Model Tag                                     |
|  - Human Approval Diff Card & Action Buttons                                          |
+---------------------------------------------------------------------------------------+
                                           | HTTP REST
                                           v
+---------------------------------------------------------------------------------------+
|                               FASTAPI APPLICATION                                     |
|                                                                                       |
|  Routers:                                                                             |
|  - /api/provider    -> Runtime provider switching, connectivity check, model tags     |
|  - /api/health      -> Provider-aware readiness, DB status, system stats              |
|  - /api/chat        -> Chat orchestrator, memory injection, approval parsing          |
|  - /api/approvals   -> Human approval lifecycle engine                                |
|  - /api/workspace   -> Sandboxed workspace explorer, patch preview, unified diffs     |
|  - /api/memory      -> Persistent semantic SQLite memory CRUD                         |
|  - /api/projects    -> Project and task organization                                  |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                              AGENT ORCHESTRATION                                      |
|                                                                                       |
|  AgentService:                                                                        |
|  1. Fetches relevant memories from SQLite via keyword indexing.                       |
|  2. Injects system base directives + active developer skill (Planner, Debugger, etc.) |
|  3. Snapshots active provider per request to prevent cross-request race conditions.   |
|  4. Calls LLMService.generate(messages, system_prompt, provider=snapshot).             |
|  5. Parses <<<PROPOSE_PATCH>>>, <<<PROPOSE_COMMAND>>>, <<<PROPOSE_TASK>>> tags.       |
|  6. Registers PENDING_APPROVAL records with diffs and risk assessments.               |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                             LLM PROVIDER ABSTRACTION                                  |
|                                                                                       |
|  LLMService.generate(provider=target_provider):                                       |
|                                                                                       |
|        [target_provider == 'ollama']                  [target_provider == 'cloud']    |
|                      |                                              |                 |
|                      v                                              v                 |
|            _generate_ollama()                             _generate_cloud()           |
|        - POST {ollama_base_url}/api/chat             - OpenAI SDK completion          |
|        - stream: false, explicit timeouts            - Nebius Token Factory / OR      |
|        - Extract message.content / thinking          - Model ID fallback handling     |
|        - Catch 404, ConnectError, Timeout            - Catch Auth, RateLimit, Timeout |
|        - RETURN (text, error)                        - RETURN (text, error)           |
|                      |                                              |                 |
|                      +-----------------------+----------------------+                 |
|                                              |                                        |
|                     NO SILENT FALLBACK (Guaranteed Isolation)                         |
+---------------------------------------------------------------------------------------+
               |                                              |
               v                                              v
+-------------------------------+              +-----------------------------------+
|      Ollama Local Daemon      |              |    Nebius Token Factory Cloud     |
|  http://127.0.0.1:11434       |              |    https://openrouter.ai/api/v1   |
|  Model: nemotron-3.5-bolt:e4b |              |    Model: nvidia/nemotron-...     |
+-------------------------------+              +-----------------------------------+
```

---

## 3. Key Design Decisions

### 3.1 Strict Isolation (No Silent Fallbacks)
When a user selects the **Local** provider, code snippets, proprietary workspace files, and chat messages are treated with utmost confidentiality. If Ollama is offline or times out:
- The system immediately returns a sanitized operational notice: `⚠️ Connection Error: Unable to reach Ollama at http://127.0.0.1:11434`.
- Under **no circumstances** does the system silently fall back to cloud inference.

### 3.2 Thread-Safe Runtime Provider Switching
The server configuration maintains an active provider (`"ollama"` or `"cloud"`) protected by a `threading.Lock`.
- When an inference request begins in `agent_service.py`, it snapshots the active provider (`settings.get_provider_snapshot()`).
- Concurrent requests remain fully isolated to their designated provider, even if a user switches provider midway through another request's execution.

### 3.3 Non-Blocking Provider Health Checks
- The `/api/provider` and `/api/health` endpoints perform a lightweight, non-blocking reachability check (`GET /api/tags`) with a strict 2.0-second timeout.
- The server will never hang or fail to boot if Ollama is temporarily stopped.
