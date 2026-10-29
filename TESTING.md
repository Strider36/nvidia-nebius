# Aegis AI — Testing Guide

This guide details the test suite, execution procedures, and verification protocols for **Aegis AI**.

---

## 1. Test Suite Overview

All unit, integration, and security tests in Aegis AI are designed to run **offline, deterministically, and cost-free**:
- **No Cloud API Credits**: Cloud inference endpoints are mocked via OpenAI client fixtures.
- **No Model Downloads Required**: Ollama HTTP calls are mocked via `httpx` fixtures.
- **Persistent DB Isolation**: Tests use temporary in-memory or throwaway SQLite databases (`tempfile.TemporaryDirectory`).

---

## 2. Test Modules

| Test File | Focus Area | Tests |
|---|---|:---:|
| [`tests/test_provider.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_provider.py) | Ollama payloads, timeouts, 404 missing model, connection errors, anti-fallback invariant, runtime switching, concurrent request isolation | 12 |
| [`tests/test_llm.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_llm.py) | Cloud OpenAI-compatible client, auth errors, timeouts, unconfigured status | 4 |
| [`tests/test_chat.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_chat.py) | Memory injection, proposal parsing (`<<<PROPOSE_PATCH>>>`, `<<<PROPOSE_COMMAND>>>`, `<<<PROPOSE_TASK>>>`), approval record generation | 5 |
| [`tests/test_health.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_health.py) | Health check structure, readiness calculation, secret and credential non-leakage | 2 |
| [`tests/test_workspace.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_workspace.py) | Workspace sandboxing, path traversal blocking, unified diffs, timestamped backups | 6 |
| [`tests/test_approvals.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_approvals.py) | Approval lifecycle (`PROPOSED -> APPROVED -> EXECUTING -> SUCCEEDED / REJECTED`), execution safety | 2 |
| [`tests/test_audit.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_audit.py) | Audit trail persistence, secret redaction in logs | 2 |
| [`tests/test_memory.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_memory.py) | Persistent SQLite semantic memory CRUD, keyword retrieval, sensitive data gateway blocking | 4 |
| [`tests/test_projects.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_projects.py) | Project and milestone task backlog management | 2 |
| [`tests/test_frontend.py`](file:///e:/Code%20Tresure/nvidia-nebius-main/nvidia-nebius-main/tests/test_frontend.py) | Static asset serving (`index.html`, `styles.css`, `app.js`), formatting elements | 3 |
| **Total** | | **42** |

---

## 3. Running Tests

### Run Entire Test Suite:
```bash
python -m pytest
```

### Run Provider Tests Only:
```bash
python -m pytest tests/test_provider.py -v
```

### Run with Coverage:
```bash
python -m pytest --cov=app -v
```
