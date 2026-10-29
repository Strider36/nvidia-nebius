"""Tests for persistent memory service and SQLite storage."""

import tempfile
from pathlib import Path
import pytest

from app.config import settings
from app.database import init_db
from app.models import MemoryCategory, MemoryCreate, MemoryUpdate
from app.services.memory_service import MemorySecurityError, MemoryService


@pytest.fixture
def temp_memory_db():
    """Setup a temporary SQLite database for memory testing."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        orig = settings.database_path
        db_file = Path(tmp_dir) / "test_memory.db"
        settings.database_path = db_file
        init_db(db_file)
        service = MemoryService()
        yield service, db_file
        settings.database_path = orig


def test_memory_creation_and_retrieval(temp_memory_db):
    """Verify creating memories across categories and keyword retrieval."""
    service, _ = temp_memory_db

    mem = service.create_memory(
        MemoryCreate(
            category=MemoryCategory.PREFERENCE,
            content="User prefers Python with type annotations and ruff formatting.",
        )
    )
    assert mem.id is not None
    assert mem.category == MemoryCategory.PREFERENCE

    # Retrieval by keyword
    results = service.retrieve_relevant_memories("annotations formatting")
    assert len(results) >= 1
    assert "type annotations" in results[0].content


def test_memory_persistence_across_reconnect(temp_memory_db):
    """Verify memories survive database connection restarts."""
    service, db_file = temp_memory_db

    mem = service.create_memory(
        MemoryCreate(
            category=MemoryCategory.INSTRUCTION,
            content="Always create tests before closing a task.",
        )
    )

    # Re-initialize service and read from the same file
    new_service = MemoryService()
    memories = new_service.list_memories(category=MemoryCategory.INSTRUCTION)
    assert any(m.id == mem.id for m in memories)


def test_memory_update_and_delete(temp_memory_db):
    """Verify memory modification and deletion."""
    service, _ = temp_memory_db

    mem = service.create_memory(
        MemoryCreate(
            category=MemoryCategory.PROJECT_CONTEXT,
            content="Initial architecture design draft.",
        )
    )

    # Update
    updated = service.update_memory(
        mem.id,
        MemoryUpdate(content="Finalized architecture design for Aegis."),
    )
    assert updated is not None
    assert "Finalized" in updated.content

    # Delete
    deleted = service.delete_memory(mem.id)
    assert deleted is True

    # Confirm deletion
    all_mems = service.list_memories()
    assert not any(m.id == mem.id for m in all_mems)


def test_sensitive_content_rejection(temp_memory_db):
    """Verify that sensitive credentials like passwords and API keys are blocked."""
    service, _ = temp_memory_db

    with pytest.raises(MemorySecurityError) as exc_info:
        service.create_memory(
            MemoryCreate(
                category=MemoryCategory.INSTRUCTION,
                content="My production password: SuperSecretPassword123!",
            )
        )
    assert "security policy violation" in str(exc_info.value).lower()

    with pytest.raises(MemorySecurityError) as exc_info:
        service.create_memory(
            MemoryCreate(
                category=MemoryCategory.PREFERENCE,
                content="Here is my api_key: sk-1234567890abcdef123456",
            )
        )
    assert "security policy violation" in str(exc_info.value).lower()

