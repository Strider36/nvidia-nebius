"""Audit logging service for Aegis AI.

Logs all sensitive operations, approvals, and execution outcomes to SQLite.
Sanitizes entries to ensure credentials and secrets are never logged.
"""

from datetime import datetime, timezone
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple
from app.database import get_db_connection
from app.models import AuditLogResponse

SECRET_REPLACERS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"(?i)(bearer\s+)([a-zA-Z0-9_\-\.]{10,})"), r"\1***REDACTED***"),
    (re.compile(r"(?i)(api[_-]?key[\s:=]+['\"]?)([a-zA-Z0-9_\-\.]{10,})(['\"]?)"), r"\1***REDACTED***\3"),
    (re.compile(r"(?i)(token[\s:=]+['\"]?)([a-zA-Z0-9_\-\.]{10,})(['\"]?)"), r"\1***REDACTED***\3"),
    (re.compile(r"(?i)(password[\s:=]+['\"]?)(.+?)(['\"])"), r"\1***REDACTED***\3"),
]


def sanitize_text(text: str) -> str:
    """Sanitize sensitive keys/tokens from log text."""
    if not text:
        return ""
    sanitized = text
    for pattern, repl in SECRET_REPLACERS:
        sanitized = pattern.sub(repl, sanitized)
    return sanitized


class AuditService:
    """Manages persistent audit records."""

    @staticmethod
    def record_event(
        action_type: str,
        proposed_operation: str,
        approval_status: str,
        execution_outcome: str,
        error_summary: Optional[str] = None,
    ) -> str:
        """Create a new audit log record."""
        log_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        clean_op = sanitize_text(proposed_operation)
        clean_err = sanitize_text(error_summary) if error_summary else None

        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO audit_logs (id, timestamp, action_type, proposed_operation, approval_status, execution_outcome, error_summary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (log_id, now, action_type, clean_op, approval_status, execution_outcome, clean_err),
            )
        return log_id

    @staticmethod
    def get_recent_logs(limit: int = 50) -> List[AuditLogResponse]:
        """Fetch recent audit log entries."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, timestamp, action_type, proposed_operation, approval_status, execution_outcome, error_summary
                FROM audit_logs
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [
                AuditLogResponse(
                    id=row["id"],
                    timestamp=row["timestamp"],
                    action_type=row["action_type"],
                    proposed_operation=row["proposed_operation"],
                    approval_status=row["approval_status"],
                    execution_outcome=row["execution_outcome"],
                    error_summary=row["error_summary"],
                )
                for row in rows
            ]


audit_service = AuditService()
