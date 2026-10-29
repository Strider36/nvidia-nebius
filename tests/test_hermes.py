"""Unit and integration tests for Hermes Agent integration in Aegis AI."""

import json
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.models import ActionType, ApprovalStatus
from app.services.hermes_service import HermesService, hermes_service
from main import app

client = TestClient(app)


def test_hermes_status_endpoint():
    """Verify GET /api/hermes/status returns valid schema and status."""
    resp = client.get("/api/hermes/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "enabled" in data
    assert "available" in data
    assert "binary_path" in data
    assert "active_provider" in data
    assert "ollama_ready" in data


def test_hermes_build_command_ollama():
    """Verify _build_command configures Ollama endpoint correctly."""
    service = HermesService()
    cmd = service._build_command("C:/fake/query.txt", provider="ollama")
    assert "chat" in cmd
    assert "--query-file" in cmd
    assert "C:/fake/query.txt" in cmd
    assert "--provider" in cmd
    assert "custom" in cmd
    assert "--base-url" in cmd
    assert f"{settings.ollama_base_url}/v1" in cmd
    assert "-m" in cmd
    assert settings.ollama_model in cmd
    assert "--format" in cmd
    assert "stream-json" in cmd
    assert "--oneshot" in cmd
    assert "--in" in cmd
    assert str(settings.workspace_path) in cmd
    assert "--toolsets" in cmd
    assert "--ignore-user-config" in cmd


def test_hermes_build_command_cloud():
    """Verify _build_command configures Cloud endpoint and API key."""
    service = HermesService()
    cmd = service._build_command("C:/fake/query.txt", provider="cloud")
    assert "--provider" in cmd
    assert "custom" in cmd
    assert "--base-url" in cmd
    assert settings.base_url in cmd
    assert "-m" in cmd
    assert settings.model_id in cmd
    if settings.api_key:
        assert "--api-key" in cmd
        assert settings.api_key in cmd


def test_hermes_generate_success():
    """Verify HermesService.generate parses stream-json output correctly."""
    service = HermesService()
    mock_jsonl = (
        '{"type": "system", "subtype": "init", "model": "test"}\n'
        '{"type": "text", "text": "Hello "}\n'
        '{"type": "text", "text": "from Hermes"}\n'
        '{"type": "result", "text": "Hello from Hermes", "exit_code": 0}\n'
    )

    mock_proc = MagicMock()
    mock_proc.stdout = mock_jsonl.splitlines(keepends=True)
    mock_proc.returncode = 0
    mock_proc.wait.return_value = 0

    with patch("subprocess.Popen", return_value=mock_proc):
        reply, err = service.generate(
            messages=[{"role": "user", "content": "Hi"}],
            system_prompt="Be concise",
            provider="ollama",
        )
        assert err is None
        assert reply == "Hello from Hermes"


def test_hermes_generate_stream():
    """Verify HermesService.generate_stream yields token chunks sequentially."""
    service = HermesService()
    mock_jsonl = (
        '{"type": "system", "subtype": "init"}\n'
        '{"type": "text", "text": "Token1 "}\n'
        '{"type": "text", "text": "Token2"}\n'
        '{"type": "result", "text": "Token1 Token2", "exit_code": 0}\n'
    )

    mock_proc = MagicMock()
    mock_proc.stdout = mock_jsonl.splitlines(keepends=True)
    mock_proc.returncode = 0
    mock_proc.poll.return_value = 0
    mock_proc.wait.return_value = 0

    with patch("subprocess.Popen", return_value=mock_proc):
        tokens = list(
            service.generate_stream(
                messages=[{"role": "user", "content": "Hi"}],
                system_prompt="Be concise",
                provider="ollama",
            )
        )
        assert tokens == ["Token1 ", "Token2"]


def test_hermes_anti_fallback_on_error():
    """Verify that Hermes errors return explicit errors and never fall back to cloud."""
    service = HermesService()
    mock_proc = MagicMock()
    mock_proc.stdout = []
    mock_proc.stderr.read.return_value = "Connection refused to Ollama"
    mock_proc.returncode = 1
    mock_proc.wait.return_value = 1

    with patch("subprocess.Popen", return_value=mock_proc):
        reply, err = service.generate(
            messages=[{"role": "user", "content": "Hi"}],
            system_prompt="Be concise",
            provider="ollama",
        )
        assert reply is None
        assert err is not None
        assert "Connection refused to Ollama" in err


def test_chat_turn_with_hermes_backend():
    """Verify POST /api/chat routes to Hermes when agent_backend='hermes'."""
    mock_reply = "I am Hermes Agent, your optional assistant."
    with patch.object(hermes_service, "generate", return_value=(mock_reply, None)) as mock_gen:
        resp = client.post(
            "/api/chat",
            json={
                "message": "Who are you?",
                "agent_backend": "hermes",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["assistant_message"] == mock_reply
        assert data["agent_backend"] == "hermes"
        assert mock_gen.called


def test_chat_turn_hermes_proposes_patch():
    """Verify that Hermes action proposals enter the human approval lifecycle."""
    mock_reply = (
        "Here is the proposed update:\n"
        '<<<PROPOSE_PATCH path="calculator.py" reason="Add multiply" risk="Low">\n'
        "def multiply(a, b):\n    return a * b\n"
        "</PROPOSE_PATCH>>>\n"
        "Please approve this patch."
    )
    with patch.object(hermes_service, "generate", return_value=(mock_reply, None)):
        resp = client.post(
            "/api/chat",
            json={
                "message": "Add multiply function",
                "agent_backend": "hermes",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "pending_approval" in data and data["pending_approval"] is not None
        assert data["pending_approval"]["target"] == "calculator.py"
        assert data["pending_approval"]["status"] == "PENDING_APPROVAL"
