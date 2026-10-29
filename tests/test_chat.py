"""Tests for chat orchestrator, tool proposal parsing, and memory injection."""

from unittest.mock import PropertyMock, patch
import tempfile
from pathlib import Path
import pytest

from app.config import settings
from app.database import init_db
from app.models import ActionType, ApprovalStatus, ChatRequest, MemoryCategory, MemoryCreate
from app.services.agent_service import agent_service
from app.services.memory_service import memory_service


@pytest.fixture
def temp_chat_env():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        orig_db = settings.database_path
        orig_ws = settings.workspace_path

        db_file = Path(tmp_dir) / "test_chat.db"
        ws_dir = Path(tmp_dir) / "workspace"
        ws_dir.mkdir(parents=True, exist_ok=True)

        settings.database_path = db_file
        settings.workspace_path = ws_dir
        init_db(db_file)

        yield
        settings.database_path = orig_db
        settings.workspace_path = orig_ws


def test_chat_memory_retrieval_and_injection(temp_chat_env):
    """Verify relevant memories are fetched and included in chat response."""
    # Seed a memory
    memory_service.create_memory(
        MemoryCreate(
            category=MemoryCategory.PREFERENCE,
            content="Owner prefers concise answers and type-annotated code.",
        )
    )

    with patch("app.services.agent_service.llm_service.generate") as mock_generate:
        mock_generate.return_value = ("I will provide type-annotated code.", None)

        res = agent_service.process_chat(
            ChatRequest(message="Can you help me write a function with annotations?")
        )

        assert not res.is_error
        assert len(res.retrieved_memories) >= 1
        assert "type-annotated" in res.retrieved_memories[0]["content"]
        assert "type-annotated" in res.assistant_message


def test_chat_patch_proposal_parsing(temp_chat_env):
    """Verify model output with PROPOSE_PATCH creates a PENDING_APPROVAL record."""
    model_output = (
        "Here is the proposed configuration file:\n"
        '<<<PROPOSE_PATCH path="config.json" reason="Create app config" risk="New file creation">\n'
        '{\n  "version": "1.0"\n}\n'
        '</PROPOSE_PATCH>>>\n'
        "Please review the changes above."
    )

    with patch("app.services.agent_service.llm_service.generate") as mock_generate:
        mock_generate.return_value = (model_output, None)

        res = agent_service.process_chat(
            ChatRequest(message="Please create config.json")
        )

        assert not res.is_error
        assert res.pending_approval is not None
        assert res.pending_approval["action_type"] == ActionType.FILE_CREATE.value
        assert res.pending_approval["target"] == "config.json"
        assert res.pending_approval["status"] == ApprovalStatus.PENDING_APPROVAL.value


def test_chat_command_proposal_parsing(temp_chat_env):
    """Verify model output with PROPOSE_COMMAND creates a command approval record."""
    model_output = (
        "Let us verify the test suite:\n"
        '<<<PROPOSE_COMMAND command="pytest -v" reason="Verify test suite" risk="Executes tests">>>>\n'
    )

    with patch("app.services.agent_service.llm_service.generate") as mock_generate:
        mock_generate.return_value = (model_output, None)

        res = agent_service.process_chat(
            ChatRequest(message="Run our tests")
        )

        assert not res.is_error
        assert res.pending_approval is not None
        assert res.pending_approval["action_type"] == ActionType.RUN_COMMAND.value
        assert res.pending_approval["target"] == "pytest -v"


def test_chat_multiple_task_proposals_parsing(temp_chat_env):
    """Verify multiple PROPOSE_TASK tags are parsed into approvals and rendered cleanly."""
    model_output = (
        "Here are suggested milestone tasks for your FastAPI web application:\n\n"
        '<<<PROPOSE_TASK title="Project Initialization" description="Initialize repository, set up virtual environment, create basic FastAPI skeleton." due_date="2025-10-02">>>\n'
        '<<<PROPOSE_TASK title="Core API Design" description="Define domain models, design routers." due_date="2025-10-16">>>\n'
        '<<<PROPOSE_TASK title="Testing Suite" description="Write comprehensive unit and integration tests." due_date="2025-11-13">>>'
    )

    with patch("app.services.agent_service.llm_service.generate") as mock_generate:
        mock_generate.return_value = (model_output, None)

        res = agent_service.process_chat(
            ChatRequest(message="Help me plan milestones for a new FastAPI web application.")
        )

        assert not res.is_error
        # Check no raw tags leak into the user message
        assert "<<<PROPOSE_TASK" not in res.assistant_message
        assert ">>>" not in res.assistant_message
        # Check clean markdown replacement
        assert "📋 **Milestone Task:** **Project Initialization**" in res.assistant_message
        assert "📅 Due: 2025-10-02" in res.assistant_message
        assert "📋 **Milestone Task:** **Core API Design**" in res.assistant_message

        # Check pending approvals
        assert res.pending_approval is not None
        assert res.pending_approval["action_type"] == ActionType.TASK_CREATE.value
        assert res.pending_approval["target"] == "Project Initialization"
        assert res.pending_approvals is not None
        assert len(res.pending_approvals) == 3
        assert res.pending_approvals[0]["target"] == "Project Initialization"
        assert res.pending_approvals[1]["target"] == "Core API Design"
        assert res.pending_approvals[2]["target"] == "Testing Suite"


def test_chat_unconfigured_model_handling(temp_chat_env):
    """Verify graceful handling when Nebius API key is not configured."""
    with patch("app.services.agent_service.llm_service.generate") as mock_gen:
        mock_gen.return_value = (None, "Nebius API key is not configured. Please set NEBIUS_API_KEY in your .env file.")
        res = agent_service.process_chat(
            ChatRequest(message="Hello Aegis")
        )
        assert res.is_error is True
        assert "not configured" in res.error_message.lower()
        assert "⚠️ Aegis AI Operational Notice" in res.assistant_message


def test_conversation_rename_endpoint(temp_chat_env):
    """Verify renaming a conversation via API."""
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)
    # Create conversation
    create_res = client.post("/api/conversations", json={"title": "Original Title"})
    assert create_res.status_code == 201
    conv_id = create_res.json()["id"]

    # Rename conversation
    patch_res = client.patch(f"/api/conversations/{conv_id}", json={"title": "Updated Title"})
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Updated Title"

    # Verify retrieval
    get_res = client.get(f"/api/conversations/{conv_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Updated Title"



