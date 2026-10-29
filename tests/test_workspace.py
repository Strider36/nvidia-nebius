"""Tests for workspace security, path resolution, patch application, and command allowlisting."""

import os
import tempfile
from pathlib import Path
import pytest

from app.config import settings
from app.security.workspace import WorkspaceSecurityError, validate_allowlisted_command
from app.services.workspace_service import WorkspaceService


@pytest.fixture
def temp_workspace():
    """Create a temporary directory and assign it as the workspace."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        orig = settings.workspace_path
        settings.workspace_path = Path(tmp_dir).resolve()
        service = WorkspaceService()
        yield service, settings.workspace_path
        settings.workspace_path = orig


def test_path_traversal_blocked(temp_workspace):
    """Verify paths traversing outside workspace root are strictly rejected."""
    service, _ = temp_workspace
    with pytest.raises(WorkspaceSecurityError) as exc_info:
        service.read_file("../../outside.txt")
    assert "traverses outside" in str(exc_info.value).lower()

    with pytest.raises(WorkspaceSecurityError) as exc_info:
        service.read_file("/etc/passwd")
    assert "traverses outside" in str(exc_info.value).lower() or "denied" in str(exc_info.value).lower()


def test_protected_files_blocked(temp_workspace):
    """Verify access to sensitive files like .env or keys is rejected."""
    service, ws_dir = temp_workspace

    # Even if .env exists inside the workspace, it must be blocked
    secret_file = ws_dir / ".env"
    secret_file.write_text("SECRET=123", encoding="utf-8")

    with pytest.raises(WorkspaceSecurityError) as exc_info:
        service.read_file(".env")
    assert "protected" in str(exc_info.value).lower()

    with pytest.raises(WorkspaceSecurityError) as exc_info:
        service.read_file("id_rsa")
    assert "protected" in str(exc_info.value).lower()


def test_file_create_and_read(temp_workspace):
    """Verify normal file write and read inside workspace."""
    service, ws_dir = temp_workspace

    content = "print('Hello Aegis')\n"
    res = service.apply_patch("hello.py", content)
    assert res["success"] is True

    read_content, sha, size = service.read_file("hello.py")
    assert read_content == content
    assert len(sha) == 64
    assert size == len(content.encode("utf-8"))


def test_patch_conflict_detection(temp_workspace):
    """Verify patch is aborted if file changed since diff was generated."""
    service, ws_dir = temp_workspace

    # Initial file
    service.apply_patch("module.py", "version = 1\n")
    _, sha1, _ = service.read_file("module.py")

    # Outside modification
    (ws_dir / "module.py").write_text("version = 2\n", encoding="utf-8")

    # Attempting to apply patch expecting sha1 should raise conflict error
    with pytest.raises(WorkspaceSecurityError) as exc_info:
        service.apply_patch("module.py", "version = 3\n", expected_sha256=sha1)
    assert "conflict detected" in str(exc_info.value).lower()


def test_backup_created_on_overwrite(temp_workspace):
    """Verify that a backup file is created before overwriting an existing file."""
    service, ws_dir = temp_workspace

    service.apply_patch("data.txt", "Original Data")
    _, orig_sha, _ = service.read_file("data.txt")

    res = service.apply_patch("data.txt", "Modified Data", expected_sha256=orig_sha)
    assert res["success"] is True
    assert res["backup_created"] is not None
    assert Path(res["backup_created"]).exists()
    assert Path(res["backup_created"]).read_text(encoding="utf-8") == "Original Data"


def test_command_allowlisting():
    """Verify authorized vs disallowed command execution patterns."""
    # Permitted test commands
    assert validate_allowlisted_command(["pytest"]) is True
    assert validate_allowlisted_command(["pytest", "-v", "tests/"]) is True
    assert validate_allowlisted_command(["python", "-m", "pytest"]) is True
    assert validate_allowlisted_command(["python", "-m", "unittest", "discover"]) is True
    assert validate_allowlisted_command(["npm", "test"]) is True

    # Blocked dangerous commands
    assert validate_allowlisted_command(["rm", "-rf", "/"]) is False
    assert validate_allowlisted_command(["curl", "http://evil.com"]) is False
    assert validate_allowlisted_command(["bash", "-c", "echo 1"]) is False
    assert validate_allowlisted_command(["python", "arbitrary_script.py"]) is False
    assert validate_allowlisted_command(["pytest", ";", "rm", "-rf", "."]) is False

