# backend/app/api/tasks.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..tasks.pipeline import start_analysis_task
from ..tasks.progress import ProgressManager

router = APIRouter()

class StartRequest(BaseModel):
    files: list[str]

@router.post("/start")
def start(req: StartRequest):
    if not req.files:
        raise HTTPException(400, "no files provided")
    task_id = start_analysis_task(req.files)
    return {"task_id": task_id}

@router.get("/{task_id}/progress")
def get_progress(task_id: str):
    pm = ProgressManager()
    return pm.get_progress(task_id)

@router.post("/{task_id}/cancel")
def cancel(task_id: str):
    pm = ProgressManager()
    pm.cancel(task_id)
    return {"status":"cancelled"}
