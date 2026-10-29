"""Tests for frontend static file serving."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_frontend_index_served():
    """Verify root path serves index.html."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Aegis AI" in response.text
    assert "Nemotron Operator" in response.text


def test_frontend_assets_served():
    """Verify styles.css and app.js are accessible."""
    css_res = client.get("/styles.css")
    assert css_res.status_code == 200
    assert "Obsidian Dark Theme" in css_res.text or ":root" in css_res.text

    js_res = client.get("/app.js")
    assert js_res.status_code == 200
    assert "Aegis AI" in js_res.text


def test_frontend_enhanced_formatting_assets():
    """Verify modern styling classes and multi-approval scripts are present."""
    css_res = client.get("/styles.css")
    assert ".approval-task-card" in css_res.text
    assert ".msg-table" in css_res.text
    assert ".btn-copy-code" in css_res.text

    js_res = client.get("/app.js")
    assert "pending_approvals" in js_res.text
    assert "approval-task-card" in js_res.text


