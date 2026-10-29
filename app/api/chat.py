"""Chat and Conversation API endpoints for Aegis AI."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
)
from app.services.agent_service import agent_service

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat_turn(req: ChatRequest) -> ChatResponse:
    """Send a message to Aegis AI and receive a structured response."""
    return agent_service.process_chat(req)


@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(project_id: Optional[str] = Query(None)) -> List[ConversationResponse]:
    """List recent conversations, optionally filtered by project."""
    return agent_service.list_conversations(project_id=project_id)


@router.post("/conversations", response_model=ConversationResponse, status_code=201)
def create_conversation(req: ConversationCreate) -> ConversationResponse:
    """Create a new conversation session."""
    return agent_service.create_conversation(title=req.title or "New Conversation", project_id=req.project_id)


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str) -> ConversationResponse:
    """Get full conversation details including messages."""
    conv = agent_service.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conv


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str):
    """Delete a conversation session."""
    deleted = agent_service.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"status": "success", "deleted_id": conversation_id}

