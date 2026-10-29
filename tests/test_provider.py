"""Comprehensive regression and security tests for Dual-Provider Inference (Ollama & Cloud).

Mocks all HTTP/API responses. Tests do not require downloading models or spending cloud credits.
Strictly verifies:
- Ollama payload, options, message extraction
- Error handling (404 missing model, connection error, timeout, malformed JSON)
- Strict provider isolation (NEVER silently fall back from local to cloud or vice-versa)
- Runtime switching via /api/provider
- Request-level provider isolation in concurrent scenarios
- Health endpoint provider-awareness and secrets redaction
- End-to-end proposal and approval parsing when using local provider
"""

import threading
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.database import init_db
from app.models import ActionType, ApprovalStatus, ChatRequest, ProviderUpdateRequest
from app.services.agent_service import agent_service
from app.services.llm_service import LLMService
from main import app

client = TestClient(app)


@pytest.fixture
def clean_test_env():
    """Isolate database, workspace, and provider settings for test execution."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        orig_db = settings.database_path
        orig_ws = settings.workspace_path
        orig_provider = settings.active_provider

        db_file = Path(tmp_dir) / "test_provider.db"
        ws_dir = Path(tmp_dir) / "workspace"
        ws_dir.mkdir(parents=True, exist_ok=True)

        settings.database_path = db_file
        settings.workspace_path = ws_dir
        init_db(db_file)

        yield

        settings.database_path = orig_db
        settings.workspace_path = orig_ws
        settings.set_provider(orig_provider)


# --- 1. Ollama Payload & Message Handling ---

def test_ollama_inference_success_and_payload():
    """Verify local inference formats messages, options, model tag, and extracts content."""
    service = LLMService(
        provider="ollama",
        ollama_base_url="http://127.0.0.1:11434",
        ollama_model="nemotron-3.5-bolt:e4b",
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.is_error = False
    mock_resp.json.return_value = {
        "model": "nemotron-3.5-bolt:e4b",
        "message": {"role": "assistant", "content": "Aegis local operator online."},
    }

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        text, err = service.generate(
            messages=[{"role": "user", "content": "Status report"}],
            system_prompt="You are Aegis AI.",
            max_tokens=512,
            temperature=0.3,
        )

        assert err is None
        assert text == "Aegis local operator online."

        # Verify exact call payload
        mock_post.assert_called_once()
        called_url = mock_post.call_args[0][0]
        assert called_url == "http://127.0.0.1:11434/api/chat"

        payload = mock_post.call_args[1]["json"]
        assert payload["model"] == "nemotron-3.5-bolt:e4b"
        assert payload["stream"] is False
        assert payload["options"]["temperature"] == 0.3
        assert payload["options"]["num_predict"] == 512
        assert len(payload["messages"]) == 2
        assert payload["messages"][0]["role"] == "system"
        assert payload["messages"][1]["role"] == "user"


def test_ollama_reasoning_fallback_extraction():
    """Verify reasoning/thinking field is extracted if message content is empty."""
    service = LLMService(provider="ollama", ollama_model="nemotron-3.5-bolt:e4b")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.is_error = False
    mock_resp.json.return_value = {
        "model": "nemotron-3.5-bolt:e4b",
        "message": {"role": "assistant", "content": "", "thinking": "Step 1: Check memory. Step 2: Formulate answer."},
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        text, err = service.generate([{"role": "user", "content": "Reason"}])
        assert err is None
        assert text == "Step 1: Check memory. Step 2: Formulate answer."


def test_ollama_streaming_inference():
    """Verify local streaming inference streams tokens line-by-line via stream=True."""
    service = LLMService(
        provider="ollama",
        ollama_base_url="http://127.0.0.1:11434",
        ollama_model="nemotron-3.5-bolt:e4b",
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.is_error = False
    mock_resp.iter_lines.return_value = [
        '{"message": {"content": "Local "}, "done": false}',
        '{"message": {"content": "Nemotron "}, "done": false}',
        '{"message": {"content": "streaming."}, "done": true}',
    ]

    mock_stream_ctx = MagicMock()
    mock_stream_ctx.__enter__.return_value = mock_resp
    mock_stream_ctx.__exit__.return_value = None

    with patch("httpx.Client.stream", return_value=mock_stream_ctx):
        tokens = list(service.generate_stream([{"role": "user", "content": "Stream test"}], provider="ollama"))
        assert tokens == ["Local ", "Nemotron ", "streaming."]



# --- 2. Ollama Error Handling ---

def test_ollama_missing_model_404():
    """Verify 404 from Ollama returns clean instructions to pull model."""
    service = LLMService(provider="ollama", ollama_model="nonexistent-model")

    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.is_error = True

    with patch("httpx.Client.post", return_value=mock_resp):
        text, err = service.generate([{"role": "user", "content": "Hi"}])
        assert text is None
        assert "model not found" in err.lower()
        assert "nonexistent-model" in err
        assert "ollama pull" in err


def test_ollama_connection_error():
    """Verify connection refusal returns informative, non-crashing error."""
    service = LLMService(provider="ollama", ollama_base_url="http://127.0.0.1:9999")

    with patch("httpx.Client.post", side_effect=httpx.ConnectError("Connection refused")):
        text, err = service.generate([{"role": "user", "content": "Hi"}])
        assert text is None
        assert "connection error" in err.lower()
        assert "ensure ollama service is running" in err.lower()


def test_ollama_timeout_handling():
    """Verify request timeouts return clear error message."""
    service = LLMService(provider="ollama")

    with patch("httpx.Client.post", side_effect=httpx.ReadTimeout("Read timed out")):
        text, err = service.generate([{"role": "user", "content": "Heavy prompt"}])
        assert text is None
        assert "request timeout" in err.lower()


def test_ollama_malformed_json_response():
    """Verify malformed JSON payload returns sanitized error."""
    service = LLMService(provider="ollama")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.is_error = False
    mock_resp.json.side_effect = ValueError("Invalid JSON in response")

    with patch("httpx.Client.post", return_value=mock_resp):
        text, err = service.generate([{"role": "user", "content": "Test"}])
        assert text is None
        assert "malformed response" in err.lower()


# --- 3. Strict Provider Isolation (No Silent Fallback) ---

def test_local_failure_never_falls_back_to_cloud():
    """CRITICAL SECURITY CONSTRAINT: A failed local request must NEVER silently route to cloud."""
    service = LLMService(
        api_key="sk-mock-cloud-key",
        provider="ollama",
        ollama_model="nemotron-3.5-bolt:e4b",
    )
    mock_cloud_client = MagicMock()
    service._client = mock_cloud_client

    with patch("httpx.Client.post", side_effect=httpx.ConnectError("Ollama offline")):
        text, err = service.generate([{"role": "user", "content": "Confidential code"}])

        # Must report local error
        assert text is None
        assert "connection error" in err.lower()

        # Cloud client must NOT have been called under any circumstance
        mock_cloud_client.chat.completions.create.assert_not_called()


def test_cloud_failure_never_falls_back_to_local():
    """A failed cloud request must not silently fall back to local without explicit user command."""
    service = LLMService(api_key="sk-mock-key", provider="cloud")
    mock_cloud_client = MagicMock()
    import openai
    mock_cloud_client.chat.completions.create.side_effect = openai.APIConnectionError(request=MagicMock())
    service._client = mock_cloud_client

    with patch("httpx.Client.post") as mock_httpx_post:
        text, err = service.generate([{"role": "user", "content": "Prompt"}])

        assert text is None
        assert "connection error" in err.lower()
        mock_httpx_post.assert_not_called()


# --- 4. Runtime Provider Switching API ---

def test_provider_api_switch_and_status(clean_test_env):
    """Verify switching provider via API changes active provider and health reporting."""
    # Switch to cloud
    resp = client.post("/api/provider", json={"provider": "cloud"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["active_provider"] == "cloud"
    assert settings.active_provider == "cloud"

    # Verify GET /api/provider matches
    get_resp = client.get("/api/provider")
    assert get_resp.status_code == 200
    assert get_resp.json()["active_provider"] == "cloud"

    # Switch back to ollama
    resp2 = client.post("/api/provider", json={"provider": "ollama"})
    assert resp2.status_code == 200
    assert resp2.json()["active_provider"] == "ollama"
    assert settings.active_provider == "ollama"

    # Invalid provider validation
    bad_resp = client.post("/api/provider", json={"provider": "invalid-provider"})
    assert bad_resp.status_code == 400
    assert "invalid provider" in bad_resp.json()["detail"].lower()


# --- 5. Concurrent Request Provider Isolation ---

def test_concurrent_requests_preserve_provider_isolation():
    """Verify concurrent requests specifying different providers execute isolatedly."""
    results = {}

    def run_request(service: LLMService, prov: str, idx: int):
        text, err = service.generate([{"role": "user", "content": "ping"}], provider=prov)
        results[f"{prov}_{idx}"] = (text, err)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.is_error = False
    mock_resp.json.return_value = {
        "model": "nemotron-3.5-bolt:e4b",
        "message": {"role": "assistant", "content": "Ollama response"},
    }

    mock_cloud_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Cloud response"
    mock_cloud_response = MagicMock(choices=[mock_choice])
    mock_cloud_client.chat.completions.create.return_value = mock_cloud_response

    service = LLMService(api_key="sk-mock", ollama_model="nemotron-3.5-bolt:e4b")
    service._client = mock_cloud_client

    with patch("httpx.Client.post", return_value=mock_resp):
        threads = []
        for i in range(4):
            p = "ollama" if i % 2 == 0 else "cloud"
            t = threading.Thread(target=run_request, args=(service, p, i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

    # Verify each request received the response for its specific provider
    for k, (text, err) in results.items():
        assert err is None
        if k.startswith("ollama"):
            assert text == "Ollama response"
        else:
            assert text == "Cloud response"



# --- 6. Health Endpoint Provider-Awareness & Secret Redaction ---

def test_health_reports_provider_without_leaking_secrets(clean_test_env):
    """Verify /api/health reflects provider readiness and never exposes API keys."""
    settings.set_provider("ollama")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "models": [{"name": "nemotron-3.5-bolt:e4b"}]
    }

    with patch("httpx.Client.get", return_value=mock_resp):
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()

        assert data["provider"] == "ollama"
        assert data["model_id"] == "nemotron-3.5-bolt:e4b"
        assert data["is_ready"] is True
        assert data["provider_status"] == "ready"

        # Security assertion: No secrets or credentials leaked
        text_dump = str(data).lower()
        assert "sk-" not in text_dump
        assert "password" not in text_dump
        assert "secret" not in text_dump


# --- 7. End-to-End Chat Proposals with Local Provider ---

def test_chat_turn_with_local_provider_generates_approval(clean_test_env):
    """Verify chat turn processed with local provider parses PROPOSE_PATCH into approval."""
    patch_output = (
        "Here is the local patch fix:\n"
        '<<<PROPOSE_PATCH path="service.py" reason="Implement local logger" risk="File creation">\n'
        'import logging\nlogger = logging.getLogger("aegis")\n'
        '</PROPOSE_PATCH>>>\n'
    )

    with patch("app.services.agent_service.llm_service.generate") as mock_gen:
        mock_gen.return_value = (patch_output, None)

        res = agent_service.process_chat(
            ChatRequest(message="Implement logger", provider="ollama")
        )

        assert not res.is_error
        assert res.pending_approval is not None
        assert res.pending_approval["action_type"] == ActionType.FILE_CREATE.value
        assert res.pending_approval["target"] == "service.py"
        assert res.pending_approval["status"] == ApprovalStatus.PENDING_APPROVAL.value

        # Verify provider parameter was forwarded to llm_service
        mock_gen.assert_called_once()
        assert mock_gen.call_args[1]["provider"] == "ollama"
