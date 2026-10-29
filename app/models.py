"""Pydantic schemas and validation models for Aegis AI."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# --- Health & Config ---
class ProviderType(str, Enum):
    OLLAMA = "ollama"
    CLOUD = "cloud"


class HealthResponse(BaseModel):
    status: str
    is_ready: bool
    model_id: str
    base_url: str
    has_api_key: bool
    database_status: str
    workspace_path: str
    host: str
    port: int
    version: str
    provider: str = "ollama"
    provider_status: Optional[str] = None
    ollama_model: Optional[str] = None
    cloud_model: Optional[str] = None


class ProviderUpdateRequest(BaseModel):
    provider: str = Field(..., description="Inference provider name ('ollama' or 'cloud')")


class ProviderStatusResponse(BaseModel):
    active_provider: str
    supported_providers: List[str]
    is_ready: bool
    status: str
    message: Optional[str] = None
    ollama_base_url: str
    ollama_model: str
    ollama_available: bool
    ollama_models: List[str] = []
    cloud_base_url: str
    cloud_model: str
    cloud_has_key: bool


# --- Memories ---
class MemoryCategory(str, Enum):
    PREFERENCE = "preference"
    PROJECT_CONTEXT = "project_context"
    INSTRUCTION = "instruction"
    SESSION_SUMMARY = "session_summary"


class MemoryCreate(BaseModel):
    category: MemoryCategory
    content: str = Field(..., min_length=2, max_length=5000)
    project_id: Optional[str] = None
    keywords: Optional[str] = None


class MemoryUpdate(BaseModel):
    category: Optional[MemoryCategory] = None
    content: Optional[str] = Field(None, min_length=2, max_length=5000)
    project_id: Optional[str] = None
    keywords: Optional[str] = None


class MemoryResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    category: MemoryCategory
    content: str
    keywords: Optional[str] = None
    created_at: str
    updated_at: str


# --- Projects & Tasks ---
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field("", max_length=2000)
    project_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    due_date: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    project_id: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    title: str
    description: str
    status: TaskStatus
    due_date: Optional[str] = None
    created_at: str
    updated_at: str


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field("", max_length=2000)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    created_at: str
    updated_at: str
    tasks: Optional[List[TaskResponse]] = None


# --- Conversations & Chat ---
class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    skill_id: Optional[str] = None
    retrieved_memories: Optional[List[Dict[str, Any]]] = None
    pending_approval_id: Optional[str] = None
    created_at: str


class ConversationCreate(BaseModel):
    title: Optional[str] = Field("New Conversation", max_length=200)
    project_id: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    title: str
    project_id: Optional[str] = None
    created_at: str
    updated_at: str
    messages: Optional[List[MessageResponse]] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    conversation_id: Optional[str] = None
    project_id: Optional[str] = None
    skill_id: Optional[str] = None
    provider: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    assistant_message: str
    retrieved_memories: List[Dict[str, Any]] = []
    pending_approval: Optional[Dict[str, Any]] = None
    pending_approvals: Optional[List[Dict[str, Any]]] = None
    suggested_skill: Optional[str] = None
    is_error: bool = False
    error_message: Optional[str] = None


# --- Approvals ---
class ApprovalStatus(str, Enum):
    PROPOSED = "PROPOSED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTING = "EXECUTING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ActionType(str, Enum):
    FILE_CREATE = "file_create"
    FILE_PATCH = "file_patch"
    RUN_COMMAND = "run_command"
    TASK_CREATE = "task_create"
    MEMORY_DELETE = "memory_delete"


class ApprovalResponse(BaseModel):
    id: str
    action_type: ActionType
    target: str
    details: Dict[str, Any]
    reason: str
    risk: str
    status: ApprovalStatus
    proposed_at: str
    resolved_at: Optional[str] = None
    result: Optional[Any] = None


class ApprovalActionRequest(BaseModel):
    decision: str = Field(..., description="'approve' or 'reject'")
    reason: Optional[str] = None


# --- Audit Logs ---
class AuditLogResponse(BaseModel):
    id: str
    timestamp: str
    action_type: str
    proposed_operation: str
    approval_status: str
    execution_outcome: str
    error_summary: Optional[str] = None


# --- Skills ---
class SkillDefinition(BaseModel):
    id: str
    name: str
    purpose: str
    instructions: str
    permitted_tools: List[str]


# --- Workspace ---
class WorkspaceFileItem(BaseModel):
    path: str
    name: str
    is_dir: bool
    size: int
    modified_at: str


class WorkspaceFileListResponse(BaseModel):
    workspace_root: str
    files: List[WorkspaceFileItem]


class WorkspaceFileReadResponse(BaseModel):
    path: str
    content: str
    size: int
    sha256: str


class WorkspacePatchProposal(BaseModel):
    path: str
    original_sha256: Optional[str] = None
    diff: str
    proposed_content: str
    reason: str


class WorkspaceCommandRequest(BaseModel):
    command: str
    reason: str

