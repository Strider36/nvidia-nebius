"""Tests for security audit trail and secret sanitization."""

import tempfile
from pathlib import Path
import pytest

from app.config import settings
from app.database import init_db
from app.services.audit_service import AuditService, sanitize_text


@pytest.fixture
def temp_audit_db():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        orig = settings.database_path
        db_file = Path(tmp_dir) / "test_audit.db"
        settings.database_path = db_file
        init_db(db_file)
        yield
        settings.database_path = orig


def test_audit_event_recording_and_retrieval(temp_audit_db):
    """Verify events are correctly stored and retrieved chronologically."""
    event_id = AuditService.record_event(
        action_type="file_patch",
        proposed_operation="patch main.py",
        approval_status="APPROVED",
        execution_outcome="SUCCEEDED",
    )
    assert event_id is not None

    logs = AuditService.get_recent_logs(limit=10)
    assert len(logs) >= 1
    assert logs[0].action_type == "file_patch"
    assert logs[0].approval_status == "APPROVED"


def test_audit_secret_sanitization():
    """Verify that credentials and tokens are redacted before logging."""
    raw = "User passed api_key='sk-abcdef1234567890abcdef' with Bearer token_secret_123456789"
    sanitized = sanitize_text(raw)

    assert "sk-abcdef1234567890abcdef" not in sanitized
    assert "token_secret_123456789" not in sanitized
    assert "REDACTED" in sanitized

