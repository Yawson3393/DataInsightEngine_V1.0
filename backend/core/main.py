"""
Main API Entrypoint
- Initializes FastAPI application
- Configures logging
- Registers API routers
- Creates WebSocket endpoints for real-time task progress
- Loads analysis plugins dynamically
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .logging_cfg import setup_logging
from .api import files, jobs, results, health
from .tasks.progress import progress_manager
from .analysis.registry import load_plugins

import uvicorn


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    # ------------------------------------------------
    # Logging (Loguru, JSON optional)
    # ------------------------------------------------
    setup_logging()

    app = FastAPI(
        title="Battery Analysis Engine",
        description="Streaming Tar.gz Pipeline → Analysis → Parquet → Web UI",
        version="1.0.0",
    )

    # ------------------------------------------------
    # CORS Setup
    # ------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------
    # Load analysis plugins (dynamic)
    # ------------------------------------------------
    load_plugins()  # Automatically load plugins from /plugins or entry_points

    # ------------------------------------------------
    # API Routers
    # ------------------------------------------------
    app.include_router(files.router, prefix="/api/files", tags=["Files"])
    app.include_router(jobs.router, prefix="/api/jobs", tags=["Tasks"])
    app.include_router(results.router, prefix="/api/results", tags=["Results"])
    app.include_router(health.router, prefix="/api/health", tags=["Health"])

    # ------------------------------------------------
    # WebSocket: Real-time progress updates
    # ------------------------------------------------
    @app.websocket("/ws/progress/{task_id}")
    async def progress_ws(websocket: WebSocket, task_id: str):
        await websocket.accept()
        progress_manager.connect(task_id, websocket)

        try:
            while True:
                # WebSocket will automatically receive pushes from manager
                await websocket.receive_text()
        except WebSocketDisconnect:
            progress_manager.disconnect(task_id, websocket)

    # ------------------------------------------------
    # (Optional) Serve frontend build
    # ------------------------------------------------
    if settings.SERVE_FRONTEND and settings.FRONTEND_DIST.exists():
        app.mount("/", StaticFiles(directory=settings.FRONTEND_DIST, html=True), name="frontend")

    return app


app = create_app()


# For local development
if __name__ == "__main__":
    uvicorn.run(
        "core.main:core",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        workers=1,
    )
