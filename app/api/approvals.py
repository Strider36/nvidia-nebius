"""Approvals API endpoints for Aegis AI Human Approval System."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models import (
    ApprovalActionRequest,
    ApprovalResponse,
    ApprovalStatus,
)
from app.services.approval_service import approval_service

router = APIRouter(prefix="/api/approvals", tags=["approvals"])


@router.get("", response_model=List[ApprovalResponse])
def list_approvals(
    status: Optional[ApprovalStatus] = Query(None, description="Filter by approval status"),
) -> List[ApprovalResponse]:
    """List all proposed actions and their approval statuses."""
    return approval_service.list_approvals(status_filter=status)


@router.get("/{approval_id}", response_model=ApprovalResponse)
def get_approval(approval_id: str) -> ApprovalResponse:
    """Get full details of a specific approval request."""
    approval = approval_service.get_approval(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found.")
    return approval


@router.post("/{approval_id}/approve", response_model=ApprovalResponse)
def approve_action(approval_id: str) -> ApprovalResponse:
    """Approve and execute a proposed action."""
    try:
        return approval_service.approve_and_execute(approval_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")


@router.post("/{approval_id}/reject", response_model=ApprovalResponse)
def reject_action(approval_id: str, req: Optional[ApprovalActionRequest] = None) -> ApprovalResponse:
    """Reject a proposed action."""
    try:
        reason = req.reason if req else None
        return approval_service.reject_action(approval_id, reason=reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

