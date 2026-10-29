"""Projects API endpoints for Aegis AI."""

from typing import List
from fastapi import APIRouter, HTTPException
from app.models import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project_service import project_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=List[ProjectResponse])
def list_projects() -> List[ProjectResponse]:
    """List all projects."""
    return project_service.list_projects()


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(data: ProjectCreate) -> ProjectResponse:
    """Create a new project."""
    return project_service.create_project(data)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str) -> ProjectResponse:
    """Get project details with associated tasks."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: str, data: ProjectUpdate) -> ProjectResponse:
    """Update project details."""
    updated = project_service.update_project(project_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found.")
    return updated


@router.delete("/{project_id}")
def delete_project(project_id: str):
    """Delete a project."""
    deleted = project_service.delete_project(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found.")
    return {"status": "success", "deleted_id": project_id}

