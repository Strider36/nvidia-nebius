"""Database layer for Aegis AI using SQLite.

Provides optimized persistent storage for memories, projects, tasks, conversations,
approvals, and audit logs with WAL mode, memory caching, and memory-mapped I/O.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional
from app.config import settings

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending',
    due_date TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    project_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    skill_id TEXT,
    retrieved_memories TEXT,
    pending_approval_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    keywords TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY,
    action_type TEXT NOT NULL,
    target TEXT NOT NULL,
    details TEXT NOT NULL,
    reason TEXT NOT NULL,
    risk TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING_APPROVAL',
    proposed_at TEXT NOT NULL,
    resolved_at TEXT,
    result TEXT
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    action_type TEXT NOT NULL,
    proposed_operation TEXT NOT NULL,
    approval_status TEXT NOT NULL,
    execution_outcome TEXT NOT NULL,
    error_summary TEXT
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_conversations_project ON conversations(project_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category);
CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project_id);
CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
"""


def get_db_path(override_path: Optional[Path] = None) -> Path:
    """Return the database file path."""
    return override_path if override_path is not None else settings.database_path


def optimize_connection(conn: sqlite3.Connection) -> None:
    """Apply high-performance Pragmas for concurrency and speed."""
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA temp_store = MEMORY;")
    conn.execute("PRAGMA cache_size = -64000;")  # 64MB cache
    conn.execute("PRAGMA mmap_size = 268435456;")  # 256MB mmap
    conn.execute("PRAGMA wal_autocheckpoint = 1000;")


def init_db(db_path: Optional[Path] = None) -> None:
    """Initialize SQLite database with required tables, indexes, and performance pragmas."""
    target_path = get_db_path(db_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(target_path), timeout=20.0) as conn:
        optimize_connection(conn)
        conn.executescript(SCHEMA_SQL)
        conn.commit()


@contextmanager
def get_db_connection(db_path: Optional[Path] = None) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for optimized SQLite connections with Row factory."""
    target_path = get_db_path(db_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path), timeout=20.0)
    conn.row_factory = sqlite3.Row
    optimize_connection(conn)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
