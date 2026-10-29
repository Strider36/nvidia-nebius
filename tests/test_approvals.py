"""Tests for Human Approval lifecycle and audit logging."""

import tempfile
from pathlib import Path
import pytest

from app.config import settings
from app.database import init_db
from app.models import ActionType, ApprovalStatus
from app.services.approval_service import ApprovalService
from app.services.audit_service import audit_service


@pytest.fixture
def temp_approval_env():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        orig_db = settings.database_path
        orig_ws = settings.workspace_path

        db_file = Path(tmp_dir) / "test_approvals.db"
        ws_dir = Path(tmp_dir) / "workspace"
        ws_dir.mkdir(parents=True, exist_ok=True)

        settings.database_path = db_file
        settings.workspace_path = ws_dir
        init_db(db_file)

        yield
        settings.database_path = orig_db
        settings.workspace_path = orig_ws


def test_approval_lifecycle_approved(temp_approval_env):
    """Verify action proposal, approval, execution, and success lifecycle."""
    # Propose file creation
    prop = ApprovalService.propose_action(
        action_type=ActionType.FILE_CREATE,
        target="script.py",
        details={"proposed_content": "print('hello')", "original_sha256": None},
        reason="Create initial script",
        risk="Low - new file",
    )
    assert prop.status == ApprovalStatus.PENDING_APPROVAL

    # Approve and execute
    result = ApprovalService.approve_and_execute(prop.id)
    assert result.status == ApprovalStatus.SUCCEEDED
    assert result.result is not None
    assert result.result.get("success") is True

    # Verify file was actually created in workspace
    created_file = settings.workspace_path / "script.py"
    assert created_file.exists()
    assert created_file.read_text() == "print('hello')"

    # Check audit logs
    logs = audit_service.get_recent_logs(limit=10)
    assert len(logs) >= 2
    outcomes = [l.execution_outcome for l in logs]
    assert "SUCCEEDED" in outcomes or "pending" in outcomes


def test_approval_lifecycle_rejected(temp_approval_env):
    """Verify rejecting a proposed action."""
    prop = ApprovalService.propose_action(
        action_type=ActionType.RUN_COMMAND,
        target="pytest",
        details={"command": "pytest"},
        reason="Run full test suite",
        risk="May take significant time",
    )
    assert prop.status == ApprovalStatus.PENDING_APPROVAL

    rejected = ApprovalService.reject_action(prop.id, reason="User does not want to run tests now")
    assert rejected.status == ApprovalStatus.REJECTED
    assert "User does not want" in rejected.result["rejected_reason"]

    # Verify invalid state transition cannot be executed
    with pytest.raises(ValueError):
        ApprovalService.approve_and_execute(prop.id)

