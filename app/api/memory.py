"""Memory API endpoints for Aegis AI."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models import (
    MemoryCategory,
    MemoryCreate,
    MemoryResponse,
    MemoryUpdate,
)
from app.services.memory_service import MemorySecurityError, memory_service

router = APIRouter(prefix="/api/memories", tags=["memory"])


@router.get("", response_model=List[MemoryResponse])
def get_memories(
    category: Optional[MemoryCategory] = Query(None),
    project_id: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Search query"),
) -> List[MemoryResponse]:
    """Retrieve memories with optional category or keyword filtering."""
    return memory_service.list_memories(
        category=category,
        project_id=project_id,
        search_query=q,
    )


@router.post("", response_model=MemoryResponse, status_code=201)
def create_memory(data: MemoryCreate) -> MemoryResponse:
    """Store a new user-approved persistent memory."""
    try:
        return memory_service.create_memory(data)
    except MemorySecurityError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{memory_id}", response_model=MemoryResponse)
def update_memory(memory_id: str, data: MemoryUpdate) -> MemoryResponse:
    """Update an existing memory item."""
    try:
        updated = memory_service.update_memory(memory_id, data)
        if not updated:
            raise HTTPException(status_code=404, detail="Memory not found.")
        return updated
    except MemorySecurityError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{memory_id}")
def delete_memory(memory_id: str):
    """Delete a memory item."""
    deleted = memory_service.delete_memory(memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found.")
    return {"status": "success", "deleted_id": memory_id}

