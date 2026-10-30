"""Human Approval lifecycle and action execution engine for Aegis AI."""

from datetime import datetime, timezone
import json
import uuid
from typing import Any, Dict, List, Optional
from app.database import get_db_connection
from app.models import ActionType, ApprovalResponse, ApprovalStatus
from app.services.audit_service import audit_service
from app.services.workspace_service import workspace_service


class ApprovalService:
    """Manages proposing, approving, rejecting, and executing sensitive actions."""

    @staticmethod
    def propose_action(
        action_type: ActionType,
        target: str,
        details: Dict[str, Any],
        reason: str,
        risk: str,
    ) -> ApprovalResponse:
        """Create a new approval request in PENDING_APPROVAL state."""
        approval_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        details_json = json.dumps(details)

        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO approvals (id, action_type, target, details, reason, risk, status, proposed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval_id,
                    action_type.value,
                    target,
                    details_json,
                    reason,
                    risk,
                    ApprovalStatus.PENDING_APPROVAL.value,
                    now,
                ),
            )

        audit_service.record_event(
            action_type=action_type.value,
            proposed_operation=f"{action_type.value} on {target}",
            approval_status=ApprovalStatus.PENDING_APPROVAL.value,
            execution_outcome="pending",
        )

        return ApprovalResponse(
            id=approval_id,
            action_type=action_type,
            target=target,
            details=details,
            reason=reason,
            risk=risk,
            status=ApprovalStatus.PENDING_APPROVAL,
            proposed_at=now,
        )

    @staticmethod
    def get_approval(approval_id: str) -> Optional[ApprovalResponse]:
        """Fetch approval details by ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, action_type, target, details, reason, risk, status, proposed_at, resolved_at, result
                FROM approvals
                WHERE id = ?
                """,
                (approval_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            return ApprovalResponse(
                id=row["id"],
                action_type=ActionType(row["action_type"]),
                target=row["target"],
                details=json.loads(row["details"]),
                reason=row["reason"],
                risk=row["risk"],
                status=ApprovalStatus(row["status"]),
                proposed_at=row["proposed_at"],
                resolved_at=row["resolved_at"],
                result=json.loads(row["result"]) if row["result"] else None,
            )

    @staticmethod
    def list_approvals(status_filter: Optional[ApprovalStatus] = None) -> List[ApprovalResponse]:
        """List all approvals, optionally filtered by status."""
        query = "SELECT id, action_type, target, details, reason, risk, status, proposed_at, resolved_at, result FROM approvals"
        params = []
        if status_filter:
            query += " WHERE status = ?"
            params.append(status_filter.value)
        query += " ORDER BY proposed_at DESC"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                ApprovalResponse(
                    id=row["id"],
                    action_type=ActionType(row["action_type"]),
                    target=row["target"],
                    details=json.loads(row["details"]),
                    reason=row["reason"],
                    risk=row["risk"],
                    status=ApprovalStatus(row["status"]),
                    proposed_at=row["proposed_at"],
                    resolved_at=row["resolved_at"],
                    result=json.loads(row["result"]) if row["result"] else None,
                )
                for row in rows
            ]

    @staticmethod
    def reject_action(approval_id: str, reason: Optional[str] = None) -> ApprovalResponse:
        """Reject a pending approval."""
        approval = ApprovalService.get_approval(approval_id)
        if not approval:
            raise ValueError(f"Approval {approval_id} not found.")

        if approval.status != ApprovalStatus.PENDING_APPROVAL:
            raise ValueError(f"Cannot reject action in state '{approval.status.value}'. Must be PENDING_APPROVAL.")

        now = datetime.now(timezone.utc).isoformat()
        result_payload = {"rejected_reason": reason or "User declined proposed action."}

        with get_db_connection() as conn:
            conn.execute(
                """
                UPDATE approvals
                SET status = ?, resolved_at = ?, result = ?
                WHERE id = ?
                """,
                (ApprovalStatus.REJECTED.value, now, json.dumps(result_payload), approval_id),
            )

        audit_service.record_event(
            action_type=approval.action_type.value,
            proposed_operation=f"{approval.action_type.value} on {approval.target}",
            approval_status=ApprovalStatus.REJECTED.value,
            execution_outcome="rejected",
            error_summary=reason,
        )

        approval.status = ApprovalStatus.REJECTED
        approval.resolved_at = now
        approval.result = result_payload
        return approval

    @staticmethod
    def approve_and_execute(approval_id: str) -> ApprovalResponse:
        """Approve and immediately execute the designated action."""
        approval = ApprovalService.get_approval(approval_id)
        if not approval:
            raise ValueError(f"Approval {approval_id} not found.")

        if approval.status != ApprovalStatus.PENDING_APPROVAL:
            raise ValueError(
                f"Cannot approve action in state '{approval.status.value}'. Must be PENDING_APPROVAL."
            )

        # Transition to EXECUTING
        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE approvals SET status = ?, resolved_at = ? WHERE id = ?",
                (ApprovalStatus.EXECUTING.value, now, approval_id),
            )

        execution_result: Dict[str, Any] = {}
        outcome_status = ApprovalStatus.SUCCEEDED
        err_msg: Optional[str] = None

        try:
            if approval.action_type in (ActionType.FILE_CREATE, ActionType.FILE_PATCH):
                path = approval.target
                content = approval.details.get("proposed_content", "")
                expected_sha = approval.details.get("original_sha256")
                execution_result = workspace_service.apply_patch(
                    relative_path=path,
                    proposed_content=content,
                    expected_sha256=expected_sha,
                )

            elif approval.action_type == ActionType.RUN_COMMAND:
                cmd = approval.details.get("command", approval.target)
                execution_result = workspace_service.execute_test_command(cmd)
                if execution_result.get("exit_code") != 0:
                    outcome_status = ApprovalStatus.FAILED
                    err_msg = execution_result.get("stderr") or f"Command exited with {execution_result.get('exit_code')}"

            elif approval.action_type == ActionType.TASK_CREATE:
                from app.services.project_service import project_service
                from app.models import TaskCreate
                created_task = project_service.create_task(
                    TaskCreate(
                        title=approval.details.get("title", approval.target),
                        description=approval.details.get("description", ""),
                        project_id=approval.details.get("project_id"),
                        due_date=approval.details.get("due_date"),
                    )
                )
                execution_result = created_task.model_dump()

            elif approval.action_type == ActionType.FILE_DELETE:
                execution_result = workspace_service.delete_path(approval.target)

            elif approval.action_type == ActionType.MEMORY_DELETE:
                from app.services.memory_service import memory_service
                deleted = memory_service.delete_memory(approval.target)
                execution_result = {"deleted": deleted, "memory_id": approval.target}

            else:
                raise ValueError(f"Unsupported action type: {approval.action_type.value}")

        except Exception as e:
            outcome_status = ApprovalStatus.FAILED
            err_msg = str(e)
            execution_result = {"error": err_msg}

        completed_at = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            conn.execute(
                """
                UPDATE approvals
                SET status = ?, resolved_at = ?, result = ?
                WHERE id = ?
                """,
                (outcome_status.value, completed_at, json.dumps(execution_result), approval_id),
            )

        audit_service.record_event(
            action_type=approval.action_type.value,
            proposed_operation=f"{approval.action_type.value} on {approval.target}",
            approval_status=ApprovalStatus.APPROVED.value,
            execution_outcome=outcome_status.value,
            error_summary=err_msg,
        )

        approval.status = outcome_status
        approval.resolved_at = completed_at
        approval.result = execution_result
        return approval

    @staticmethod
    def execute_action_autonomously(
        action_type: ActionType,
        target: str,
        details: Dict[str, Any],
        reason: str,
        risk: str,
    ) -> Tuple[ApprovalResponse, Dict[str, Any]]:
        """Execute a permitted routine action autonomously with full safety validation, backups, and audit logging."""
        approval_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        details_json = json.dumps(details)

        outcome_status = ApprovalStatus.SUCCEEDED
        err_msg: Optional[str] = None
        execution_result: Dict[str, Any] = {}

        try:
            if action_type in (ActionType.FILE_CREATE, ActionType.FILE_PATCH):
                path = target
                content = details.get("proposed_content", "")
                expected_sha = details.get("original_sha256")
                execution_result = workspace_service.apply_patch(
                    relative_path=path,
                    proposed_content=content,
                    expected_sha256=expected_sha,
                )
            elif action_type == ActionType.RUN_COMMAND:
                cmd = details.get("command", target)
                execution_result = workspace_service.execute_test_command(cmd)
                if execution_result.get("exit_code") != 0:
                    outcome_status = ApprovalStatus.FAILED
                    err_msg = execution_result.get("stderr") or f"Command exited with {execution_result.get('exit_code')}"
            elif action_type == ActionType.TASK_CREATE:
                from app.services.project_service import project_service
                from app.models import TaskCreate
                created_task = project_service.create_task(
                    TaskCreate(
                        title=details.get("title", target),
                        description=details.get("description", ""),
                        project_id=details.get("project_id"),
                        due_date=details.get("due_date"),
                    )
                )
                execution_result = created_task.model_dump()
            else:
                raise ValueError(f"High-risk action '{action_type.value}' cannot be executed autonomously.")
        except Exception as e:
            outcome_status = ApprovalStatus.FAILED
            err_msg = str(e)
            execution_result = {"error": err_msg}

        completed_at = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO approvals (id, action_type, target, details, reason, risk, status, proposed_at, resolved_at, result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval_id,
                    action_type.value,
                    target,
                    details_json,
                    reason,
                    risk,
                    outcome_status.value,
                    now,
                    completed_at,
                    json.dumps(execution_result),
                ),
            )

        audit_service.record_event(
            action_type=action_type.value,
            proposed_operation=f"Autonomous {action_type.value} on {target}",
            approval_status=ApprovalStatus.APPROVED.value,
            execution_outcome=outcome_status.value,
            error_summary=err_msg,
        )

        appr = ApprovalResponse(
            id=approval_id,
            action_type=action_type,
            target=target,
            details=details,
            reason=reason,
            risk=risk,
            status=outcome_status,
            proposed_at=now,
            resolved_at=completed_at,
            result=execution_result,
        )
        return appr, execution_result


approval_service = ApprovalService()

