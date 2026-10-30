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


def test_chat_turn_hermes_supervised_mode():
    """Verify Scenario 9: Switch to supervised mode — existing approval workflow works."""
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
                "execution_mode": "supervised",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "pending_approval" in data and data["pending_approval"] is not None
        assert data["pending_approval"]["target"] == "calculator.py"
        assert data["pending_approval"]["status"] == "PENDING_APPROVAL"


def test_scenario_1_hermes_inspect_project_no_approval():
    """Verify Scenario 1: Ask Hermes to inspect the project — completes without approval."""
    mock_reply = "I have inspected the project workspace. Found 3 files: main.py, utils.py, and tests."
    with patch.object(hermes_service, "generate", return_value=(mock_reply, None)):
        resp = client.post(
            "/api/chat",
            json={
                "message": "Inspect the project and tell me what files exist",
                "agent_backend": "hermes",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["pending_approval"] is None
        assert data["pending_approvals"] is None
        assert "inspected the project" in data["assistant_message"]


def test_scenario_2_hermes_create_file_autonomous():
    """Verify Scenario 2: Ask Hermes to create a file — automatically executed without approval dialog."""
    test_rel_path = "auto_created_script.py"
    target_file = settings.workspace_path / test_rel_path
    if target_file.exists():
        target_file.unlink()

    mock_reply = (
        f'<<<PROPOSE_PATCH path="{test_rel_path}" reason="Auto-create helper" risk="Low">\n'
        'def auto_run():\n    return "Aegis Hermes Autonomous"\n'
        '</PROPOSE_PATCH>>>\n'
        'Created the helper file.'
    )
    with patch.object(hermes_service, "generate", return_value=(mock_reply, None)):
        resp = client.post(
            "/api/chat",
            json={
                "message": f"Create {test_rel_path}",
                "agent_backend": "hermes",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        # In autonomous mode, no pending approval dialog is generated
        assert data["pending_approval"] is None
        assert data["executed_actions"] is not None
        assert len(data["executed_actions"]) == 1
        assert data["executed_actions"][0]["target"] == test_rel_path
        # File is actually created on disk
        assert target_file.exists()
        assert "Aegis Hermes Autonomous" in target_file.read_text(encoding="utf-8")


def test_scenario_3_hermes_fix_bug_autonomous():
    """Verify Scenario 3: Ask Hermes to fix a bug — automatically applies authorized workspace edits."""
    bug_rel_path = "math_ops.py"
    bug_file = settings.workspace_path / bug_rel_path
    bug_file.write_text("def subtract(a, b):\n    return a + b\n", encoding="utf-8")

    mock_reply = (
        f'<<<PROPOSE_PATCH path="{bug_rel_path}" reason="Fix subtract subtraction logic" risk="Low">\n'
        'def subtract(a, b):\n    return a - b\n'
        '</PROPOSE_PATCH>>>\n'
        'I fixed the bug in subtract.'
    )
    with patch.object(hermes_service, "generate", return_value=(mock_reply, None)):
        resp = client.post(
            "/api/chat",
            json={
                "message": f"Fix the bug in {bug_rel_path}",
                "agent_backend": "hermes",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["pending_approval"] is None
        assert bug_file.read_text(encoding="utf-8").strip() == "def subtract(a, b):\n    return a - b"


def test_scenario_4_hermes_run_tests_autonomous():
    """Verify Scenario 4: Ask Hermes to run tests — allowlisted tests run without human approval."""
    mock_reply = (
        '<<<PROPOSE_COMMAND command="python -m unittest" reason="Run test suite" risk="Low">>>\n'
        'Ran the test suite.'
    )
    with patch.object(hermes_service, "generate", return_value=(mock_reply, None)):
        with patch("app.services.workspace_service.workspace_service.execute_test_command", return_value={"command": "python -m unittest", "exit_code": 0, "stdout": "OK", "stderr": ""}):
            resp = client.post(
                "/api/chat",
                json={
                    "message": "Run tests",
                    "agent_backend": "hermes",
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["pending_approval"] is None
            assert data["executed_actions"] is not None
            assert data["executed_actions"][0]["target"] == "python -m unittest"
            assert "Autonomous Execution" in data["assistant_message"]


def test_scenario_5_hermes_modify_multiple_files_autonomous():
    """Verify Scenario 5: Ask Hermes to modify multiple files — all complete automatically."""
    file1_path = settings.workspace_path / "module_a.py"
    file2_path = settings.workspace_path / "module_b.py"

    mock_reply = (
        '<<<PROPOSE_PATCH path="module_a.py" reason="Module A update" risk="Low">\n'
        'ALPHA = 1\n'
        '</PROPOSE_PATCH>>>\n'
        '<<<PROPOSE_PATCH path="module_b.py" reason="Module B update" risk="Low">\n'
        'BETA = 2\n'
        '</PROPOSE_PATCH>>>\n'
        'Both modules updated.'
    )
    with patch.object(hermes_service, "generate", return_value=(mock_reply, None)):
        resp = client.post(
            "/api/chat",
            json={
                "message": "Update module A and module B",
                "agent_backend": "hermes",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["pending_approval"] is None
        assert len(data["executed_actions"]) == 2
        assert file1_path.exists()
        assert file2_path.exists()
        assert "ALPHA = 1" in file1_path.read_text(encoding="utf-8")
        assert "BETA = 2" in file2_path.read_text(encoding="utf-8")


def test_scenario_6_hermes_delete_directory_approval_required():
    """Verify Scenario 6: Deleting an important directory requires explicit human approval."""
    mock_reply = (
        '<<<PROPOSE_DELETE path="critical_subfolder" reason="Clean up old directory" risk="High">>>\n'
        'Proposed deletion of critical_subfolder.'
    )
    with patch.object(hermes_service, "generate", return_value=(mock_reply, None)):
        resp = client.post(
            "/api/chat",
            json={
                "message": "Delete critical_subfolder directory",
                "agent_backend": "hermes",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        # Deletion is high-risk: MUST require approval
        assert data["pending_approval"] is not None
        assert data["pending_approval"]["action_type"] == "file_delete"
        assert data["pending_approval"]["target"] == "critical_subfolder"
        assert data["pending_approval"]["status"] == "PENDING_APPROVAL"


def test_scenario_7_hermes_access_outside_workspace_blocked():
    """Verify Scenario 7: Accessing files outside the workspace is strictly blocked."""
    mock_reply = (
        '<<<PROPOSE_PATCH path="../../outside_sandbox.txt" reason="Escape" risk="High">\n'
        'HACK\n'
        '</PROPOSE_PATCH>>>\n'
    )
    with patch.object(hermes_service, "generate", return_value=(mock_reply, None)):
        resp = client.post(
            "/api/chat",
            json={
                "message": "Write outside workspace",
                "agent_backend": "hermes",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        # Security violation is blocked
        assert data["pending_approval"] is None
        assert (data.get("executed_actions") or []) == []
        outside_file = settings.workspace_path.parent / "outside_sandbox.txt"
        assert not outside_file.exists()


def test_scenario_8_hermes_expose_api_keys_blocked():
    """Verify Scenario 8: Accessing .env or secret patterns is blocked."""
    mock_reply = (
        '<<<PROPOSE_PATCH path=".env" reason="Overwrite secrets" risk="High">\n'
        'OPENROUTER_API_KEY=stolen_key\n'
        '</PROPOSE_PATCH>>>\n'
    )
    with patch.object(hermes_service, "generate", return_value=(mock_reply, None)):
        resp = client.post(
            "/api/chat",
            json={
                "message": "Modify .env",
                "agent_backend": "hermes",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["pending_approval"] is None
        assert (data.get("executed_actions") or []) == []


def test_scenario_10_native_aegis_behavior_unchanged():
    """Verify Scenario 10: Switch to Nemotron/Aegis native — existing supervised behavior is preserved."""
    mock_reply = (
        '<<<PROPOSE_PATCH path="native_module.py" reason="Aegis edit" risk="Low">\n'
        'print("Native Aegis")\n'
        '</PROPOSE_PATCH>>>\n'
        'Please approve this change.'
    )
    with patch("app.services.agent_service.llm_service.generate", return_value=(mock_reply, None)):
        resp = client.post(
            "/api/chat",
            json={
                "message": "Create native module",
                "agent_backend": "aegis",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        # Aegis native reasoning defaults to supervised mode
        assert data["execution_mode"] == "supervised"
        assert data["pending_approval"] is not None
        assert data["pending_approval"]["target"] == "native_module.py"
        assert data["pending_approval"]["status"] == "PENDING_APPROVAL"
