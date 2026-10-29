"""Health check endpoint for Aegis AI."""

from fastapi import APIRouter
from app import __version__
from app.config import settings
from app.database import get_db_connection
from app.models import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return application health, system status, and provider configuration readiness.

    Never exposes secrets or API keys. Non-blocking lightweight checks.
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

    active = settings.active_provider
    provider_status = "degraded"
    provider_ready = False

    if active == "ollama":
        from app.api.provider import check_ollama_status
        ollama_ok, ollama_models, _ = check_ollama_status()
        if not ollama_ok:
            provider_status = "offline"
            provider_ready = False
        else:
            target = settings.ollama_model.lower()
            model_found = any(
                m.lower() == target or m.lower().startswith(f"{target}:") or target.startswith(f"{m.lower()}:")
                for m in ollama_models
            )
            if model_found:
                provider_status = "ready"
                provider_ready = True
            else:
                provider_status = "model_missing"
                provider_ready = False
    else:  # cloud
        if settings.is_cloud_configured:
            provider_status = "ready"
            provider_ready = True
        else:
            provider_status = "unconfigured"
            provider_ready = False

    is_ready = provider_ready and (db_status == "connected")
    overall_status = "ready" if is_ready else ("degraded" if db_status == "connected" else "error")

    return HealthResponse(
        status=overall_status,
        is_ready=is_ready,
        model_id=settings.active_model_id,
        base_url=settings.active_base_url,
        has_api_key=settings.is_configured,
        database_status=db_status,
        workspace_path=str(settings.workspace_path),
        host=settings.host,
        port=settings.port,
        version=__version__,
        provider=active,
        provider_status=provider_status,
        ollama_model=settings.ollama_model,
        cloud_model=settings.model_id,
    )


