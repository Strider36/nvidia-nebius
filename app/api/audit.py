"""Audit Log API endpoints for Aegis AI."""

from typing import List
from fastapi import APIRouter, Query
from app.models import AuditLogResponse
from app.services.audit_service import audit_service

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=List[AuditLogResponse])
def get_audit_logs(limit: int = Query(50, ge=1, le=200)) -> List[AuditLogResponse]:
    """Retrieve recent audit events for transparency and security monitoring."""
    return audit_service.get_recent_logs(limit=limit)

