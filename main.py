"""Main application entry point for Aegis AI with performance optimizations."""

from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app import __version__
from app.config import get_resource_path, settings
from app.database import init_db
from app.api.health import router as health_router
from app.api.chat import router as chat_router
from app.api.memory import router as memory_router
from app.api.projects import router as projects_router
from app.api.tasks import router as tasks_router
from app.api.skills import router as skills_router
from app.api.approvals import router as approvals_router
from app.api.audit import router as audit_router
from app.api.workspace import router as workspace_router
from app.api.provider import router as provider_router
from app.api.hermes import router as hermes_router

# Locate frontend assets dynamically for both source and bundled builds
FRONTEND_DIR = get_resource_path("frontend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    settings.ensure_directories()
    init_db()
    yield


app = FastAPI(
    title="Aegis AI",
    description="Private Personal AI Operator with Persistent Memory, Safe Workspace, and Approvals",
    version=__version__,
    lifespan=lifespan,
)

# Compression middleware for fast JSON payloads and static assets (>1KB)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Localhost CORS protection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_and_performance_headers(request: Request, call_next):
    """Inject security headers and process timing on all responses."""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time

    # Performance metric header
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"

    # Security hardening headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Static asset caching policy
    if request.url.path.endswith((".css", ".js", ".svg", ".png", ".woff2")):
        response.headers["Cache-Control"] = "public, max-age=3600"

    return response


# Register API routers
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(memory_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(skills_router)
app.include_router(approvals_router)
app.include_router(audit_router)
app.include_router(workspace_router)
app.include_router(provider_router)
app.include_router(hermes_router)

# Mount frontend static files
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


def start() -> None:
    """CLI / Wheel package entry point."""
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    start()
