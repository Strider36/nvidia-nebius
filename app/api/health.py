"""Health check endpoint for Aegis AI."""

from fastapi import APIRouter
from app import __version__
from app.config import settings
from app.database import get_db_connection
from app.models import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return application health, system status, and configuration readiness.

    Never exposes secrets or API keys.
    """
    db_status = "disconnected"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            if cursor.fetchone():
                db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"

    is_ready = settings.is_configured and (db_status == "connected")
    overall_status = "ready" if is_ready else ("degraded" if db_status == "connected" else "error")

    return HealthResponse(
        status=overall_status,
        is_ready=is_ready,
        model_id=settings.nebius_model_id,
        base_url=settings.nebius_base_url,
        has_api_key=settings.is_configured,
        database_status=db_status,
        workspace_path=str(settings.workspace_path),
        host=settings.host,
        port=settings.port,
        version=__version__,
    )

