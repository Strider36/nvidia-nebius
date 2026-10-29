"""Skill service for loading and managing explicit reusable skills."""

from pathlib import Path
from typing import Dict, List, Optional
import yaml
from app.config import get_resource_path
from app.models import SkillDefinition

SKILLS_DIR = get_resource_path("skills")


class SkillService:
    """Manages system skills loaded from explicit definition files."""

    def __init__(self, skills_dir: Optional[Path] = None) -> None:
        self.skills_dir = skills_dir or SKILLS_DIR
        self._skills: Dict[str, SkillDefinition] = {}
        self.reload_skills()

    def reload_skills(self) -> None:
        """Scan skills directory and parse markdown definitions."""
        self._skills.clear()
        if not self.skills_dir.exists():
            return

        for md_file in self.skills_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter_raw = parts[1]
                    body = parts[2].strip()
                    try:
                        meta = yaml.safe_load(frontmatter_raw)
                        skill = SkillDefinition(
                            id=meta.get("id", md_file.stem),
                            name=meta.get("name", md_file.stem),
                            purpose=meta.get("purpose", ""),
                            instructions=body,
                            permitted_tools=meta.get("permitted_tools", []),
                        )
                        self._skills[skill.id] = skill
                    except Exception:
                        continue

    def list_skills(self) -> List[SkillDefinition]:
        """Return list of all registered skills."""
        return list(self._skills.values())

    def get_skill(self, skill_id: str) -> Optional[SkillDefinition]:
        """Retrieve a skill by its identifier."""
        return self._skills.get(skill_id)


skill_service = SkillService()

