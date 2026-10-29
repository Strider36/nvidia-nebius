"""Workspace API endpoints for Aegis AI."""

from fastapi import APIRouter, HTTPException, Query
from app.config import settings
from app.models import (
    ActionType,
    ApprovalResponse,
    WorkspaceFileListResponse,
    WorkspaceFileReadResponse,
    WorkspaceCommandRequest,
)
from app.security.workspace import WorkspaceSecurityError, validate_allowlisted_command
from app.services.approval_service import approval_service
from app.services.workspace_service import workspace_service
import shlex

router = APIRouter(prefix="/api/workspace", tags=["workspace"])


@router.get("/files", response_model=WorkspaceFileListResponse)
def list_workspace_files(subpath: str = Query("", description="Relative subpath")):
    """List permitted files in workspace directory."""
    try:
        files = workspace_service.list_files(subpath)
        return WorkspaceFileListResponse(
            workspace_root=str(settings.workspace_path),
            files=files,
        )
    except WorkspaceSecurityError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/file", response_model=WorkspaceFileReadResponse)
def read_workspace_file(path: str = Query(..., description="Relative file path")):
    """Read a permitted workspace text file."""
    try:
        content, sha256, size = workspace_service.read_file(path)
        return WorkspaceFileReadResponse(
            path=path,
            content=content,
            size=size,
            sha256=sha256,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: '{path}'")
    except WorkspaceSecurityError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/command", response_model=ApprovalResponse)
def propose_test_command(req: WorkspaceCommandRequest) -> ApprovalResponse:
    """Propose running an allowlisted test command.

    Requires user approval before execution.
    """
    try:
        parts = shlex.split(req.command)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid command syntax: {str(e)}")

    if not validate_allowlisted_command(parts):
        raise HTTPException(
            status_code=400,
            detail="Command is not in allowlist. Permitted: pytest, python -m pytest, python -m unittest, npm test, node --test.",
        )

    return approval_service.propose_action(
        action_type=ActionType.RUN_COMMAND,
        target=req.command,
        details={"command": req.command},
        reason=req.reason or "Run allowlisted workspace tests",
        risk="Executes test runner inside workspace sandbox",
    )

