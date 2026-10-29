"""Provider management and runtime switching endpoints for Aegis AI.

Supports switching between local Ollama inference and Cloud inference (Nebius/OpenRouter).
Never exposes API keys or secrets.
"""

from typing import Any, Dict, List, Tuple
from fastapi import APIRouter, HTTPException
import httpx
from app.config import settings
from app.models import ProviderStatusResponse, ProviderUpdateRequest

router = APIRouter(prefix="/api", tags=["provider"])


def check_ollama_status() -> Tuple[bool, List[str], str]:
    """Check Ollama connectivity and installed models with a strict 2s timeout.

    Returns:
        Tuple of (is_available, installed_model_names, error_or_status_message).
    """
    url = f"{settings.ollama_base_url.rstrip('/')}/api/tags"
    try:
        with httpx.Client(timeout=2.0) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
                return True, models, "Connected"
            return False, [], f"HTTP {resp.status_code}"
    except httpx.ConnectError:
        return False, [], "Unable to connect to Ollama (connection refused)"
    except httpx.TimeoutException:
        return False, [], "Ollama health check timed out"
    except Exception as e:
        return False, [], f"Ollama check error: {str(e)[:60]}"


def build_provider_status() -> ProviderStatusResponse:
    """Build current provider status snapshot without exposing secrets."""
    active = settings.active_provider
    ollama_ok, ollama_models, ollama_msg = check_ollama_status()

    # Determine status & readiness
    if active == "ollama":
        if not ollama_ok:
            status = "offline"
            is_ready = False
            msg = f"Ollama unreachable at {settings.ollama_base_url}: {ollama_msg}"
        else:
            # Check if configured model exists (exact or base name match)
            target = settings.ollama_model.lower()
            model_found = any(
                m.lower() == target or m.lower().startswith(f"{target}:") or target.startswith(f"{m.lower()}:")
                for m in ollama_models
            )
            if model_found:
                status = "ready"
                is_ready = True
                msg = f"Local Nemotron ready on Ollama ({settings.ollama_model})"
            else:
                status = "model_missing"
                is_ready = False
                msg = f"Model '{settings.ollama_model}' not found in Ollama. Available: {', '.join(ollama_models[:3]) or 'none'}"
    else:  # cloud
        has_key = settings.is_cloud_configured
        if has_key:
            status = "ready"
            is_ready = True
            msg = f"Cloud provider ready ({settings.model_id})"
        else:
            status = "unconfigured"
            is_ready = False
            msg = "Cloud API key is missing. Set OPENROUTER_API_KEY or NEBIUS_API_KEY in .env."

    return ProviderStatusResponse(
        active_provider=active,
        supported_providers=["ollama", "cloud"],
        is_ready=is_ready,
        status=status,
        message=msg,
        ollama_base_url=settings.ollama_base_url,
        ollama_model=settings.ollama_model,
        ollama_available=ollama_ok,
        ollama_models=ollama_models,
        cloud_base_url=settings.base_url,
        cloud_model=settings.model_id,
        cloud_has_key=settings.is_cloud_configured,
    )


@router.get("/provider", response_model=ProviderStatusResponse)
def get_provider() -> ProviderStatusResponse:
    """Get active provider configuration and connectivity status."""
    return build_provider_status()


@router.post("/provider", response_model=ProviderStatusResponse)
def switch_provider(req: ProviderUpdateRequest) -> ProviderStatusResponse:
    """Switch the active inference provider at runtime ('ollama' or 'cloud')."""
    clean_provider = (req.provider or "").strip().lower()
    if clean_provider not in ("ollama", "cloud"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider '{req.provider}'. Allowed providers: 'ollama', 'cloud'.",
        )

    settings.set_provider(clean_provider)
    return build_provider_status()
