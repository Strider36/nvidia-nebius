"""Project and task persistence and management service for Aegis AI."""

from datetime import datetime, timezone
import uuid
from typing import List, Optional
from app.database import get_db_connection
from app.models import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    TaskCreate,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)


class ProjectService:
    """Manages projects and tasks."""

    @staticmethod
    def create_project(data: ProjectCreate) -> ProjectResponse:
        project_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO projects (id, name, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, data.name, data.description or "", now, now),
            )
        return ProjectResponse(
            id=project_id,
            name=data.name,
            description=data.description or "",
            created_at=now,
            updated_at=now,
            tasks=[],
        )

    @staticmethod
    def list_projects() -> List[ProjectResponse]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, created_at, updated_at FROM projects ORDER BY updated_at DESC")
            rows = cursor.fetchall()

            projects: List[ProjectResponse] = []
            for r in rows:
                p_id = r["id"]
                # Fetch tasks for project
                cursor.execute(
                    """
                    SELECT id, project_id, title, description, status, due_date, created_at, updated_at
                    FROM tasks
                    WHERE project_id = ?
                    ORDER BY created_at ASC
                    """,
                    (p_id,),
                )
                task_rows = cursor.fetchall()
                tasks = [
                    TaskResponse(
                        id=tr["id"],
                        project_id=tr["project_id"],
                        title=tr["title"],
                        description=tr["description"],
                        status=TaskStatus(tr["status"]),
                        due_date=tr["due_date"],
                        created_at=tr["created_at"],
                        updated_at=tr["updated_at"],
                    )
                    for tr in task_rows
                ]
                projects.append(
                    ProjectResponse(
                        id=p_id,
                        name=r["name"],
                        description=r["description"],
                        created_at=r["created_at"],
                        updated_at=r["updated_at"],
                        tasks=tasks,
                    )
                )
            return projects

    @staticmethod
    def get_project(project_id: str) -> Optional[ProjectResponse]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, description, created_at, updated_at FROM projects WHERE id = ?",
                (project_id,),
            )
            r = cursor.fetchone()
            if not r:
                return None

            cursor.execute(
                """
                SELECT id, project_id, title, description, status, due_date, created_at, updated_at
                FROM tasks
                WHERE project_id = ?
                ORDER BY created_at ASC
                """,
                (project_id,),
            )
            tasks = [
                TaskResponse(
                    id=tr["id"],
                    project_id=tr["project_id"],
                    title=tr["title"],
                    description=tr["description"],
                    status=TaskStatus(tr["status"]),
                    due_date=tr["due_date"],
                    created_at=tr["created_at"],
                    updated_at=tr["updated_at"],
                )
                for tr in cursor.fetchall()
            ]
            return ProjectResponse(
                id=r["id"],
                name=r["name"],
                description=r["description"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
                tasks=tasks,
            )

    @staticmethod
    def update_project(project_id: str, data: ProjectUpdate) -> Optional[ProjectResponse]:
        current = ProjectService.get_project(project_id)
        if not current:
            return None

        new_name = data.name if data.name is not None else current.name
        new_desc = data.description if data.description is not None else current.description
        now = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            conn.execute(
                """
                UPDATE projects
                SET name = ?, description = ?, updated_at = ?
                WHERE id = ?
                """,
                (new_name, new_desc, now, project_id),
            )
        return ProjectService.get_project(project_id)

    @staticmethod
    def delete_project(project_id: str) -> bool:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            return cursor.rowcount > 0

    # --- Task operations ---
    @staticmethod
    def create_task(data: TaskCreate) -> TaskResponse:
        task_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO tasks (id, project_id, title, description, status, due_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    data.project_id,
                    data.title,
                    data.description or "",
                    data.status.value,
                    data.due_date,
                    now,
                    now,
                ),
            )
        return TaskResponse(
            id=task_id,
            project_id=data.project_id,
            title=data.title,
            description=data.description or "",
            status=data.status,
            due_date=data.due_date,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def list_tasks(project_id: Optional[str] = None) -> List[TaskResponse]:
        query = "SELECT id, project_id, title, description, status, due_date, created_at, updated_at FROM tasks"
        params = []
        if project_id:
            query += " WHERE project_id = ?"
            params.append(project_id)
        query += " ORDER BY created_at DESC"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                TaskResponse(
                    id=r["id"],
                    project_id=r["project_id"],
                    title=r["title"],
                    description=r["description"],
                    status=TaskStatus(r["status"]),
                    due_date=r["due_date"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"],
                )
                for r in rows
            ]

    @staticmethod
    def update_task(task_id: str, data: TaskUpdate) -> Optional[TaskResponse]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, project_id, title, description, status, due_date, created_at, updated_at FROM tasks WHERE id = ?",
                (task_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            new_title = data.title if data.title is not None else row["title"]
            new_desc = data.description if data.description is not None else row["description"]
            new_status = data.status.value if data.status is not None else row["status"]
            new_project_id = data.project_id if data.project_id is not None else row["project_id"]
            new_due_date = data.due_date if data.due_date is not None else row["due_date"]
            now = datetime.now(timezone.utc).isoformat()

            conn.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, status = ?, project_id = ?, due_date = ?, updated_at = ?
                WHERE id = ?
                """,
                (new_title, new_desc, new_status, new_project_id, new_due_date, now, task_id),
            )

        return TaskResponse(
            id=task_id,
            project_id=new_project_id,
            title=new_title,
            description=new_desc,
            status=TaskStatus(new_status),
            due_date=new_due_date,
            created_at=row["created_at"],
            updated_at=now,
        )

    @staticmethod
    def delete_task(task_id: str) -> bool:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0


project_service = ProjectService()

