"""Security constraints and path resolution for Aegis AI Workspace."""

from pathlib import Path
from typing import List, Tuple
from app.config import settings

# Disallowed file names and patterns that must never be read or written
BLOCKED_PATTERNS = [
    ".env",
    ".env.",
    "id_rsa",
    "id_ed25519",
    ".git",
    ".pem",
    ".key",
    ".pfx",
    ".p12",
    "credentials",
    "secrets",
    "authorized_keys",
]


class WorkspaceSecurityError(Exception):
    """Raised when an operation violates workspace security boundaries."""
    pass


def is_path_blocked(path_obj: Path) -> bool:
    """Check if file or any parent directory in path is blocked."""
    for part in path_obj.parts:
        lower_part = part.lower()
        for pattern in BLOCKED_PATTERNS:
            if pattern in lower_part:
                return True
    return False


def validate_workspace_path(path_str: str) -> Path:
    """Validate and resolve a path within the configured workspace.

    Guarantees:
    - Path must reside strictly inside AEGIS_WORKSPACE.
    - No path traversal (../) escaping the root.
    - Rejects unauthorized absolute paths outside workspace.
    - Rejects protected/blocked files.
    """
    if not path_str or not path_str.strip():
        return settings.workspace_path.resolve()

    raw = path_str.strip()
    workspace_root = settings.workspace_path.resolve()

    p = Path(raw)
    if p.is_absolute():
        resolved = p.resolve()
        try:
            resolved.relative_to(workspace_root)
        except ValueError:
            raise WorkspaceSecurityError(
                f"Access denied: Absolute path '{raw}' is outside authorized workspace root."
            )
    else:
        resolved = (workspace_root / raw).resolve()
        try:
            resolved.relative_to(workspace_root)
        except ValueError:
            raise WorkspaceSecurityError(
                f"Access denied: Path '{raw}' traverses outside authorized workspace root."
            )

    if is_path_blocked(resolved):
        raise WorkspaceSecurityError(
            f"Access denied: Path '{raw}' matches protected security patterns."
        )

    return resolved


ALLOWLISTED_COMMAND_PREFIXES: List[Tuple[str, ...]] = [
    ("pytest",),
    ("python", "-m", "pytest"),
    ("python", "-m", "unittest"),
    ("npm", "test"),
    ("node", "--test"),
    ("ruff",),
    ("python", "-m", "ruff"),
    ("flake8",),
    ("python", "-m", "flake8"),
    ("mypy",),
    ("python", "-m", "mypy"),
    ("git", "status"),
    ("git", "diff"),
    ("python", "-m", "py_compile"),
]


def validate_allowlisted_command(command_parts: List[str]) -> bool:
    """Verify that command matches the strict allowlist."""
    if not command_parts:
        return False

    for prefix in ALLOWLISTED_COMMAND_PREFIXES:
        if len(command_parts) >= len(prefix):
            if tuple(command_parts[:len(prefix)]) == prefix:
                # Additional check: disallow shell operators or semicolons in arguments
                for arg in command_parts:
                    if any(char in arg for char in [";", "&", "|", "`", "$", ">", "<"]):
                        return False
                return True
    return False
