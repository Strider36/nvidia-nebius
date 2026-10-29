"""Persistent Memory service for Aegis AI using SQLite.

Supports categorization (preference, project_context, instruction, session_summary),
keyword-based retrieval, search, and sensitive data guardrails.
"""

from datetime import datetime, timezone
import re
import uuid
from typing import List, Optional
from app.database import get_db_connection
from app.models import MemoryCategory, MemoryCreate, MemoryResponse, MemoryUpdate

SENSITIVE_DETECTORS = [
    re.compile(r"(?i)\b(password|passwd|pwd)\b[\s:=]+"),
    re.compile(r"(?i)\b(api[_-]?key|secret|auth[_-]?token)\b[\s:=]+"),
    re.compile(r"(?i)\b(bearer\s+[a-zA-Z0-9_\-\.]{15,})\b"),
    re.compile(r"(?i)\b(private[_-]?key)\b"),
]

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "have", "are", "was",
    "were", "will", "would", "should", "could", "about", "into", "over", "after",
    "can", "you", "help", "please", "write", "make", "what", "where", "when", "how"
}


class MemorySecurityError(Exception):
    """Raised when an attempt is made to store sensitive data in semantic memory."""
    pass


class MemoryService:
    """Operations for persistent memory."""

    @staticmethod
    def _validate_content_safety(content: str) -> None:
        """Enforce guardrails: Never store credentials or sensitive tokens in memory."""
        for pattern in SENSITIVE_DETECTORS:
            if pattern.search(content):
                raise MemorySecurityError(
                    "Security policy violation: Sensitive data (passwords, API keys, tokens) must never be stored in persistent memory."
                )

    @staticmethod
    def _extract_keywords(content: str, custom_keywords: Optional[str] = None) -> str:
        """Extract indexing keywords and token stems from text."""
        raw_words = re.findall(r"\b[a-zA-Z0-9]{3,}\b", content.lower())
        filtered = [w for w in raw_words if w not in STOPWORDS]
        # Also include 4-char prefixes for substring matching
        stems = [w[:4] for w in filtered if len(w) >= 5]
        all_tokens = set(filtered + stems)

        if custom_keywords:
            for k in custom_keywords.split(","):
                clean_k = k.strip().lower()
                if clean_k and clean_k not in STOPWORDS:
                    all_tokens.add(clean_k)

        return " ".join(sorted(all_tokens))

    @staticmethod
    def create_memory(data: MemoryCreate) -> MemoryResponse:
        """Store a new memory item."""
        MemoryService._validate_content_safety(data.content)
        memory_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        keywords = MemoryService._extract_keywords(data.content, data.keywords)

        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO memories (id, project_id, category, content, keywords, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory_id,
                    data.project_id,
                    data.category.value,
                    data.content.strip(),
                    keywords,
                    now,
                    now,
                ),
            )

        return MemoryResponse(
            id=memory_id,
            project_id=data.project_id,
            category=data.category,
            content=data.content.strip(),
            keywords=keywords,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def list_memories(
        category: Optional[MemoryCategory] = None,
        project_id: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 100,
    ) -> List[MemoryResponse]:
        """Query memories with optional filtering by category, project, or keyword search."""
        query = "SELECT id, project_id, category, content, keywords, created_at, updated_at FROM memories WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category.value)
        if project_id:
            query += " AND (project_id = ? OR project_id IS NULL)"
            params.append(project_id)
        if search_query and search_query.strip():
            tokens = [t.strip().lower() for t in search_query.split() if t.strip()]
            for token in tokens:
                query += " AND (content LIKE ? OR keywords LIKE ?)"
                params.extend([f"%{token}%", f"%{token}%"])

        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                MemoryResponse(
                    id=r["id"],
                    project_id=r["project_id"],
                    category=MemoryCategory(r["category"]),
                    content=r["content"],
                    keywords=r["keywords"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"],
                )
                for r in rows
            ]

    @staticmethod
    def retrieve_relevant_memories(
        query: str,
        project_id: Optional[str] = None,
        limit: int = 5,
    ) -> List[MemoryResponse]:
        """Keyword-based retrieval of memories relevant to a query."""
        if not query or not query.strip():
            return []

        tokens = [t.lower() for t in re.findall(r"\b[a-zA-Z0-9]{3,}\b", query) if t.lower() not in STOPWORDS]
        if not tokens:
            return []

        # Find memories matching any of the significant query terms or stems
        clauses = []
        params = []
        for token in tokens[:8]:
            clauses.append("(content LIKE ? OR keywords LIKE ?)")
            params.extend([f"%{token}%", f"%{token}%"])
            # If word is long, also match stem
            if len(token) >= 5:
                clauses.append("(keywords LIKE ?)")
                params.append(f"%{token[:4]}%")

        base_sql = f"SELECT id, project_id, category, content, keywords, created_at, updated_at FROM memories WHERE ({' OR '.join(clauses)})"
        if project_id:
            base_sql += " AND (project_id = ? OR project_id IS NULL)"
            params.append(project_id)

        base_sql += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(base_sql, params)
            rows = cursor.fetchall()
            return [
                MemoryResponse(
                    id=r["id"],
                    project_id=r["project_id"],
                    category=MemoryCategory(r["category"]),
                    content=r["content"],
                    keywords=r["keywords"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"],
                )
                for r in rows
            ]

    @staticmethod
    def update_memory(memory_id: str, data: MemoryUpdate) -> Optional[MemoryResponse]:
        """Update an existing memory."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, project_id, category, content, keywords, created_at, updated_at FROM memories WHERE id = ?",
                (memory_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            new_content = data.content.strip() if data.content is not None else row["content"]
            MemoryService._validate_content_safety(new_content)

            new_category = data.category.value if data.category is not None else row["category"]
            new_project_id = data.project_id if data.project_id is not None else row["project_id"]
            new_keywords = (
                MemoryService._extract_keywords(new_content, data.keywords)
                if (data.content is not None or data.keywords is not None)
                else row["keywords"]
            )
            now = datetime.now(timezone.utc).isoformat()

            conn.execute(
                """
                UPDATE memories
                SET project_id = ?, category = ?, content = ?, keywords = ?, updated_at = ?
                WHERE id = ?
                """,
                (new_project_id, new_category, new_content, new_keywords, now, memory_id),
            )

        return MemoryResponse(
            id=memory_id,
            project_id=new_project_id,
            category=MemoryCategory(new_category),
            content=new_content,
            keywords=new_keywords,
            created_at=row["created_at"],
            updated_at=now,
        )

    @staticmethod
    def delete_memory(memory_id: str) -> bool:
        """Delete a memory item."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            return cursor.rowcount > 0


memory_service = MemoryService()
