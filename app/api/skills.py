"""Skills API endpoints for Aegis AI."""

from typing import List
from fastapi import APIRouter
from app.models import SkillDefinition
from app.services.skill_service import skill_service

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("", response_model=List[SkillDefinition])
def get_skills() -> List[SkillDefinition]:
    """List available reusable skills."""
    return skill_service.list_skills()

