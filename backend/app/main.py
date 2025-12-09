# backend/app/main.py
import os, asyncio
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .api import files, tasks, analysis
from .utils.logger import logger
from .tasks.progress import ProgressManager

app = FastAPI(title="BatteryInsightEngine", version="0.1")

# CORS
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# include routers
app.include_router(files.router, prefix="/api/files", tags=["Files"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])

# mount frontend (static)
if os.path.isdir("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# websocket progress
@app.websocket("/ws/progress")
async def ws_progress(ws: WebSocket):
    await ws.accept()
    pm = ProgressManager()
    try:
        while True:
            snapshot = pm.get_progress_snapshot()
            await ws.send_json(snapshot)
            await asyncio.sleep(0.5)
    except Exception:
        await ws.close()
