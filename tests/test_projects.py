"""Tests for project and task management and persistence."""

import tempfile
from pathlib import Path
import pytest

from app.config import settings
from app.database import init_db
from app.models import ProjectCreate, ProjectUpdate, TaskCreate, TaskStatus, TaskUpdate
from app.services.project_service import ProjectService


@pytest.fixture
def temp_project_db():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        orig = settings.database_path
        db_file = Path(tmp_dir) / "test_projects.db"
        settings.database_path = db_file
        init_db(db_file)
        yield
        settings.database_path = orig


def test_project_crud(temp_project_db):
    """Verify creating, listing, updating, and deleting projects."""
    # Create
    p = ProjectService.create_project(
        ProjectCreate(name="Nemotron Operator", description="Autonomous agent development")
    )
    assert p.id is not None
    assert p.name == "Nemotron Operator"

    # List
    projects = ProjectService.list_projects()
    assert len(projects) == 1
    assert projects[0].id == p.id

    # Update
    updated = ProjectService.update_project(
        p.id,
        ProjectUpdate(description="Updated description with testing phase"),
    )
    assert updated.description == "Updated description with testing phase"

    # Delete
    deleted = ProjectService.delete_project(p.id)
    assert deleted is True
    assert len(ProjectService.list_projects()) == 0


def test_task_crud_and_status(temp_project_db):
    """Verify creating, querying, updating task statuses."""
    p = ProjectService.create_project(ProjectCreate(name="Core Infrastructure"))

    # Create Task
    task = ProjectService.create_task(
        TaskCreate(
            project_id=p.id,
            title="Configure Nebius Token Factory",
            description="Add API credentials to local .env",
            status=TaskStatus.PENDING,
            due_date="2026-11-01",
        )
    )
    assert task.id is not None
    assert task.status == TaskStatus.PENDING

    # Update Task Status
    updated = ProjectService.update_task(
        task.id,
        TaskUpdate(status=TaskStatus.IN_PROGRESS),
    )
    assert updated.status == TaskStatus.IN_PROGRESS

    # Verify tasks are returned in project response
    project_with_tasks = ProjectService.get_project(p.id)
    assert len(project_with_tasks.tasks) == 1
    assert project_with_tasks.tasks[0].id == task.id

