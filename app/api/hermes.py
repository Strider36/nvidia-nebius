"""Hermes Agent API router for Aegis AI.

Provides status, readiness inspection, and configuration endpoints for Hermes Agent.
"""

from fastapi import APIRouter
from app.models import HermesStatusResponse
from app.services.hermes_service import hermes_service

router = APIRouter(prefix="/api/hermes", tags=["hermes"])


@router.get("/status", response_model=HermesStatusResponse)
def get_hermes_status() -> HermesStatusResponse:
    """Check Hermes Agent installation, binary availability, and backend readiness."""
    status_info = hermes_service.get_status()
    return HermesStatusResponse(**status_info)
