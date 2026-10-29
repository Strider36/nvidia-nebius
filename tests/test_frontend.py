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


def test_frontend_chatgpt_redesign_elements():
    """Verify ChatGPT-inspired UI elements, welcome copy, suggestion chips, and responsive classes."""
    html_res = client.get("/")
    assert html_res.status_code == 200
    assert "How can I help you build today?" in html_res.text
    assert "Plan a Project" in html_res.text
    assert "Explain Code" in html_res.text
    assert "Debug an Issue" in html_res.text
    assert "Generate Tests" in html_res.text
    assert "conversationSearchInput" in html_res.text
    assert "btnToggleSidebar" in html_res.text
    assert "chat-textarea" in html_res.text

    css_res = client.get("/styles.css")
    assert css_res.status_code == 200
    assert ".suggestion-chip" in css_res.text
    assert ".composer-container" in css_res.text
    assert ".btn-msg-action" in css_res.text
    assert ".sidebar.collapsed" in css_res.text

    js_res = client.get("/app.js")
    assert js_res.status_code == 200
    assert "handleCopyAssistantMessage" in js_res.text
    assert "handleRetryLastMessage" in js_res.text
    assert "groupConversationsByDate" in js_res.text


def test_frontend_response_experience_and_syntax_highlighting():
    """Verify v0.4.0 premium response experience, syntax highlighter, and cancellation UI."""
    html_res = client.get("/")
    assert html_res.status_code == 200
    assert "btnStop" in html_res.text
    assert "toastContainer" in html_res.text

    css_res = client.get("/styles.css")
    assert css_res.status_code == 200
    assert ".code-block-wrapper" in css_res.text
    assert ".code-block-header" in css_res.text
    assert ".tok-keyword" in css_res.text
    assert ".tok-string" in css_res.text
    assert ".tok-comment" in css_res.text
    assert ".toast" in css_res.text
    assert ".msg-table-wrapper" in css_res.text
    assert "prefers-reduced-motion" in css_res.text

    js_res = client.get("/app.js")
    assert js_res.status_code == 200
    assert "highlightSyntax" in js_res.text
    assert "renderSafeMarkdown" in js_res.text
    assert "currentAbortController" in js_res.text
    assert "copyToClipboard" in js_res.text
    assert "showToast" in js_res.text
    assert "sanitizeUrl" in js_res.text


def test_frontend_obsidian_violet_design_system_and_motion():
    """Verify v0.5.0 Obsidian & Electric Violet tokens, motion system, and SVG suggestion chips."""
    html_res = client.get("/")
    assert html_res.status_code == 200
    # Confirm clean geometric SVGs inside suggestion chips (no emoji glyphs)
    assert 'class="chip-icon"' in html_res.text
    assert '<polyline points="16 18 22 12 16 6">' in html_res.text

    css_res = client.get("/styles.css")
    assert css_res.status_code == 200
    # Core color tokens
    assert "#0B0C0F" in css_res.text
    assert "#101116" in css_res.text
    assert "#15171D" in css_res.text
    assert "#1B1D25" in css_res.text
    assert "#E6E4EC" in css_res.text
    assert "#A2A2AF" in css_res.text
    assert "#777986" in css_res.text
    assert "#A78BFA" in css_res.text
    assert "#B9A5FF" in css_res.text
    assert "#292B32" in css_res.text
    assert "#62C9A0" in css_res.text
    assert "#E7B96A" in css_res.text
    assert "#F07878" in css_res.text
    # Motion tokens and keyframes
    assert "--ease-out" in css_res.text
    assert "--duration-fast" in css_res.text
    assert "heroEntrance" in css_res.text
    assert "chipEntrance" in css_res.text


def test_frontend_streaming_assets():
    """Verify v0.6.0 native SSE token streaming assets and DOM handlers are present."""
    css_res = client.get("/styles.css")
    assert css_res.status_code == 200
    assert ".stream-content" in css_res.text
    assert ".streaming-cursor" in css_res.text
    assert "streamBlink" in css_res.text

    js_res = client.get("/app.js")
    assert js_res.status_code == 200
    assert "createStreamingMessageRow" in js_res.text
    assert "createMessageActionsBar" in js_res.text
    assert "/api/chat/stream" in js_res.text
    assert "abortCurrentRequest" in js_res.text


def test_frontend_unified_design_system_and_settings():
    """Verify v0.7.0 unified design system tokens, shared components, SVG close buttons, and Settings view."""
    html_res = client.get("/")
    assert html_res.status_code == 200
    # Settings modal and triggers
    assert 'id="modalSettings"' in html_res.text
    assert 'id="btnOpenSettingsModal"' in html_res.text
    assert 'id="btnTopbarSettings"' in html_res.text
    assert 'id="btnRunDiagnostics"' in html_res.text
    # Accessible geometric SVG close buttons in all modal headers (no raw &times;)
    assert 'class="btn-close" data-close-modal title="Close modal" aria-label="Close modal">' in html_res.text
    assert "&times;</button>" not in html_res.text  # Confirm all raw &times; close entities are eliminated

    css_res = client.get("/styles.css")
    assert css_res.status_code == 200
    # Typography scale
    assert "--font-size-2xs" in css_res.text
    assert "--font-size-xs" in css_res.text
    assert "--font-size-sm" in css_res.text
    assert "--font-size-base" in css_res.text
    assert "--font-size-md" in css_res.text
    assert "--font-size-lg" in css_res.text
    # Spacing scale
    assert "--space-3xs" in css_res.text
    assert "--space-xs" in css_res.text
    assert "--space-sm" in css_res.text
    assert "--space-md" in css_res.text
    assert "--space-xl" in css_res.text
    # Shared components
    assert ".status-pill" in css_res.text
    assert ".status-pill-dot" in css_res.text
    assert ".data-table" in css_res.text
    assert ".mono-time" in css_res.text
    assert ".approval-item-card" in css_res.text
    assert ".settings-card" in css_res.text
    assert ".empty-state-icon" in css_res.text

    js_res = client.get("/app.js")
    assert js_res.status_code == 200
    assert "loadSettingsModal" in js_res.text
    assert "btnOpenSettingsModal" in js_res.text
    assert "btnRunDiagnostics" in js_res.text







