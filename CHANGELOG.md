# Changelog

All notable changes to **Aegis AI** are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
