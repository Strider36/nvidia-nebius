"""Tests for Aegis AI health and configuration endpoints."""

import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

from app.config import Settings
from app.database import init_db
from main import app

client = TestClient(app)


def test_health_endpoint_structure():
    """Verify health endpoint returns valid structure without leaking credentials."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "is_ready" in data
    assert "model_id" in data
    assert "base_url" in data
    assert "has_api_key" in data
    assert "database_status" in data
    assert "workspace_path" in data
    assert "version" in data

    # Security check: Never leak actual secrets
    assert "sk-" not in str(data)
    assert "password" not in str(data).lower()
    assert "secret" not in str(data).lower()


def test_missing_model_configuration():
    """Verify system reports degraded readiness when API key is empty."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        test_db = Path(tmp_dir) / "test.db"
        init_db(test_db)
        
        test_settings = Settings()
        test_settings.nebius_api_key = None
        assert not test_settings.is_configured
