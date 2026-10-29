"""Workspace service providing sandboxed file access, diffing, and test execution."""

import difflib
import hashlib
from datetime import datetime, timezone
import os
from pathlib import Path
import shlex
import subprocess
from typing import Any, Dict, List, Optional, Tuple
from app.config import settings
from app.models import WorkspaceFileItem
from app.security.workspace import (
    WorkspaceSecurityError,
    validate_allowlisted_command,
    validate_workspace_path,
)


class WorkspaceService:
    """Operations restricted to the designated workspace."""

    def __init__(self) -> None:
        self.backup_dir = settings.workspace_path.resolve() / ".aegis_backups"

    def list_files(self, subpath: str = "") -> List[WorkspaceFileItem]:
        """List files and folders within the permitted workspace directory."""
        target_dir = validate_workspace_path(subpath)
        if not target_dir.exists() or not target_dir.is_dir():
            return []

        results: List[WorkspaceFileItem] = []
        workspace_root = settings.workspace_path.resolve()

        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != ".aegis_backups"]

            for file_name in files:
                if file_name.startswith("."):
                    continue
                file_path = Path(root) / file_name
                try:
                    rel = str(file_path.relative_to(workspace_root)).replace("\\", "/")
                    validated = validate_workspace_path(rel)
                    stat = validated.stat()
                    results.append(
                        WorkspaceFileItem(
                            path=rel,
                            name=file_name,
                            is_dir=False,
                            size=stat.st_size,
                            modified_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                        )
                    )
                except WorkspaceSecurityError:
                    continue

        return results

    def read_file(self, relative_path: str) -> Tuple[str, str, int]:
        """Read a file within the workspace.

        Returns (content, sha256_hash, size_in_bytes).
        """
        target_path = validate_workspace_path(relative_path)
        if not target_path.exists() or not target_path.is_file():
            raise FileNotFoundError(f"File not found: '{relative_path}'")

        stat = target_path.stat()
        if stat.st_size > settings.max_file_size_bytes:
            raise WorkspaceSecurityError(
                f"File size {stat.st_size} bytes exceeds maximum permitted size of {settings.max_file_size_bytes} bytes."
            )

        content = target_path.read_text(encoding="utf-8", errors="replace")
        content_bytes = content.encode("utf-8")
        sha256 = hashlib.sha256(content_bytes).hexdigest()
        return content, sha256, len(content_bytes)

    def compute_diff(self, original: str, modified: str, filename: str) -> str:
        """Produce a standard unified diff between original and modified content."""
        orig_lines = original.splitlines(keepends=True)
        mod_lines = modified.splitlines(keepends=True)
        diff_lines = list(
            difflib.unified_diff(
                orig_lines,
                mod_lines,
                fromfile=f"a/{filename}",
                tofile=f"b/{filename}",
            )
        )
        return "".join(diff_lines)

    def apply_patch(
        self,
        relative_path: str,
        proposed_content: str,
        expected_sha256: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Apply an approved file change with backup and conflict detection."""
        target_path = validate_workspace_path(relative_path)
        backup_path_str: Optional[str] = None

        if target_path.exists() and target_path.is_file():
            current_content = target_path.read_text(encoding="utf-8", errors="replace")
            current_sha256 = hashlib.sha256(current_content.encode("utf-8")).hexdigest()

            # Conflict Detection
            if expected_sha256 and current_sha256 != expected_sha256:
                raise WorkspaceSecurityError(
                    f"Conflict detected: File '{relative_path}' has been modified since proposed diff was generated. Patch rejected."
                )

            # Create backup
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"{timestamp}_{target_path.name}.bak"
            backup_file.write_text(current_content, encoding="utf-8", newline="\n")
            backup_path_str = str(backup_file)
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)

        target_path.write_text(proposed_content, encoding="utf-8", newline="\n")
        new_sha256 = hashlib.sha256(proposed_content.encode("utf-8")).hexdigest()

        return {
            "success": True,
            "path": relative_path,
            "backup_created": backup_path_str,
            "new_sha256": new_sha256,
        }

    def execute_test_command(self, command_str: str) -> Dict[str, Any]:
        """Run an explicitly allowlisted test command inside the workspace."""
        try:
            parts = shlex.split(command_str)
        except Exception as e:
            raise WorkspaceSecurityError(f"Invalid command syntax: {str(e)}")

        if not validate_allowlisted_command(parts):
            raise WorkspaceSecurityError(
                f"Command '{command_str}' is not in the authorized test allowlist. Permitted commands: pytest, python -m pytest, python -m unittest, npm test, node --test."
            )

        workspace_root = settings.workspace_path.resolve()

        try:
            proc = subprocess.run(
                parts,
                cwd=str(workspace_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20.0,
                shell=False,
            )
            return {
                "command": command_str,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "timed_out": False,
            }
        except subprocess.TimeoutExpired:
            return {
                "command": command_str,
                "exit_code": -1,
                "stdout": "",
                "stderr": "Command execution timed out after 20 seconds.",
                "timed_out": True,
            }
        except Exception as e:
            return {
                "command": command_str,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Execution failed: {str(e)}",
                "timed_out": False,
            }


workspace_service = WorkspaceService()
