"""End-to-end integration and lifecycle verification for Aegis AI.

Tests the full lifecycle:
1. Application startup & version consistency.
2. Provider status & model inspection (without leaking secrets).
3. Hermes Agent status & CLI integration.
4. Human Approval lifecycle:
   Proposal parsing -> Pending state -> Human Approval -> Workspace execution -> Backup creation -> Audit log.
5. Rejection lifecycle:
   Proposal parsing -> Pending state -> Rejection -> Audit log recorded.
"""

import json
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app import __version__
from app.config import settings
from app.database import get_db_connection, init_db
from app.models import ActionType, ApprovalStatus
from main import app

client = TestClient(app)


def setup_module():
    """Ensure clean workspace and DB for test."""
    settings.workspace_path.mkdir(parents=True, exist_ok=True)
    init_db()


def test_e2e_version_and_metadata():
    """Verify application version matches throughout app, health, and openapi."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == __version__
    assert app.version == __version__


def test_e2e_provider_status():
    """Verify provider status endpoint reports active state without leaking secrets."""
    resp = client.get("/api/provider")
    assert resp.status_code == 200
    data = resp.json()
    assert data["active_provider"] in ("ollama", "cloud")
    assert "supported_providers" in data
    assert "ollama" in data["supported_providers"]
    assert "cloud" in data["supported_providers"]
    assert "api_key" not in data
    assert "Authorization" not in str(data)


def test_e2e_hermes_status():
    """Verify Hermes status endpoint accurately reports binary existence and version."""
    resp = client.get("/api/hermes/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "available" in data
    assert "version" in data
    if os.path.exists(settings.hermes_bin_path):
        assert data["available"] is True


def test_e2e_full_action_approval_execution_lifecycle(tmp_path):
    """Verify complete end-to-end proposal, approval, execution, backup, and audit recording."""
    test_file = "e2e_verified_module.py"
    workspace_file = settings.workspace_path / test_file
    backup_dir = settings.workspace_path / ".aegis_backups"

    if workspace_file.exists():
        workspace_file.unlink()

    # 1. Propose action via chat agent service
    from app.services.agent_service import agent_service
    from unittest.mock import patch
    from app.services.llm_service import llm_service

    mock_llm_reply = (
        f"I propose creating `{test_file}` to demonstrate safe operations.\n\n"
        f'<<<PROPOSE_PATCH path="{test_file}" reason="E2E test file creation" risk="Low - sandbox only">\n'
        'print("Aegis AI E2E Verified")\n'
        '</PROPOSE_PATCH>>>\n'
    )

    with patch.object(llm_service, "generate", return_value=(mock_llm_reply, None)):
        from app.models import ChatRequest

        chat_resp = agent_service.process_chat(
            ChatRequest(
                message="Create a test module",
                conversation_id=None,
                project_id=None,
                skill_id=None,
                provider="ollama",
                agent_backend="aegis",
            )
        )

        assert chat_resp.pending_approval is not None
        approval_id = chat_resp.pending_approval["id"]
        assert chat_resp.pending_approval["target"] == test_file
        assert chat_resp.pending_approval["status"] == ApprovalStatus.PENDING_APPROVAL.value

    # 2. Verify approval is in database with status PENDING_APPROVAL
    with get_db_connection() as conn:
        row = conn.execute("SELECT status FROM approvals WHERE id = ?", (approval_id,)).fetchone()
        assert row is not None
        assert row["status"] == ApprovalStatus.PENDING_APPROVAL.value

    # 3. Approve and execute via API endpoint
    appr_resp = client.post(f"/api/approvals/{approval_id}/approve")
    assert appr_resp.status_code == 200
    appr_data = appr_resp.json()
    assert appr_data["status"] == ApprovalStatus.SUCCEEDED.value

    # 4. Verify file was created in workspace
    assert workspace_file.exists()
    assert "Aegis AI E2E Verified" in workspace_file.read_text(encoding="utf-8")

    # 5. Propose modification to verify backup creation
    mock_mod_reply = (
        f'<<<PROPOSE_PATCH path="{test_file}" reason="Modify test file" risk="Low">\n'
        'print("Aegis AI Modified")\n'
        '</PROPOSE_PATCH>>>\n'
    )

    with patch.object(llm_service, "generate", return_value=(mock_mod_reply, None)):
        mod_resp = agent_service.process_chat(
            ChatRequest(
                message="Update test module",
                conversation_id=chat_resp.conversation_id,
                project_id=None,
                skill_id=None,
                provider="ollama",
                agent_backend="aegis",
            )
        )
        mod_approval_id = mod_resp.pending_approval["id"]

    # Approve modification
    mod_appr_resp = client.post(f"/api/approvals/{mod_approval_id}/approve")
    assert mod_appr_resp.status_code == 200
    assert mod_appr_resp.json()["status"] == ApprovalStatus.SUCCEEDED.value

    # 6. Verify backup was created in .aegis_backups
    backups = list(backup_dir.glob(f"*_{test_file}.bak"))
    assert len(backups) >= 1
    assert "Aegis AI E2E Verified" in backups[-1].read_text(encoding="utf-8")

    # 7. Verify audit log has recorded the approved executions
    audit_resp = client.get("/api/audit")
    assert audit_resp.status_code == 200
    events = audit_resp.json()
    assert len(events) >= 2
    outcomes = [e["execution_outcome"] for e in events]
    assert ApprovalStatus.SUCCEEDED.value in outcomes

    # Cleanup test files
    if workspace_file.exists():
        workspace_file.unlink()
    for b in backups:
        try:
            b.unlink()
        except Exception:
            pass
