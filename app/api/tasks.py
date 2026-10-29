"""Tasks API endpoints for Aegis AI."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models import TaskCreate, TaskResponse, TaskUpdate
from app.services.project_service import project_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskResponse])
def list_tasks(project_id: Optional[str] = Query(None)) -> List[TaskResponse]:
    """List tasks, optionally filtered by project."""
    return project_service.list_tasks(project_id=project_id)


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(data: TaskCreate) -> TaskResponse:
    """Create a new task."""
    return project_service.create_task(data)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, data: TaskUpdate) -> TaskResponse:
    """Update task status or attributes."""
    updated = project_service.update_task(task_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found.")
    return updated


@router.delete("/{task_id}")
def delete_task(task_id: str):
    """Delete a task."""
    deleted = project_service.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found.")
    return {"status": "success", "deleted_id": task_id}

