from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

from ..pipeline.dispatcher import Dispatcher
from ..pipeline.worker_pool import JobStatus
from ..logging_cfg import get_task_logger

router = APIRouter()

# 全局 dispatcher
dispatcher = Dispatcher()

# -----------------------------
# 请求模型
# -----------------------------
class JobRequest(BaseModel):
    files: list[str]  # tar.gz 文件列表
    config_override: Optional[dict] = None


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str = ""


# -----------------------------
# API
# -----------------------------
@router.post("/start", response_model=JobResponse)
def start_job(req: JobRequest):
    """
    启动一个新任务：
    - ingest
    - align
    - analyze
    streaming 模式多进程执行
    """
    log = get_task_logger()

    try:
        job_id = dispatcher.create_job(
            input_files=req.files,
            config_override=req.config_override,
        )

        log.info(f"Job started: {job_id}")

        return JobResponse(job_id=job_id, status="queued", message="Job accepted")

    except Exception as e:
        log.error(f"Failed to start job: {e}")
        raise HTTPException(500, f"Failed to start job: {e}")


@router.get("/{job_id}", response_model=Dict)
def get_job_status(job_id: str):
    """
    查询任务状态（queue / running / finished / error）
    """
    job = dispatcher.get_job(job_id)
    if job is None:
        raise HTTPException(404, f"Job not found: {job_id}")

    return {
        "job_id": job_id,
        "status": job.status.value,
        "progress": job.progress,
        "message": job.message,
        "errors": job.errors,
    }


@router.post("/{job_id}/cancel", response_model=JobResponse)
def cancel_job(job_id: str):
    """
    取消任务
    """
    try:
        dispatcher.cancel_job(job_id)
        return JobResponse(
            job_id=job_id,
            status="cancelled",
            message="Job cancelled",
        )
    except Exception as e:
        raise HTTPException(400, f"Cancel failed: {e}")
# /api/jobs - 启动/取消/状态