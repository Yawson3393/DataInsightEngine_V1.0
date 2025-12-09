import multiprocessing as mp
from multiprocessing.pool import Pool
from enum import Enum
from dataclasses import dataclass, field
import time
from typing import Dict, Optional, Any

from .worker_process import worker_entry
from ..logging_cfg import get_task_logger


# ------------------------------
# Job Status Enum
# ------------------------------
class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"
    CANCELLED = "cancelled"


# ------------------------------
# Job Record (each task metadata)
# ------------------------------
@dataclass
class JobRecord:
    job_id: str
    files: list
    config: dict
    status: JobStatus = JobStatus.QUEUED
    progress: dict = field(default_factory=dict)
    message: str = ""
    errors: list = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None


# ------------------------------
# Worker Pool
# ------------------------------
class WorkerPool:

    def __init__(self, max_workers: int = None):
        """
        A CPU parallel pool for processing CSV streams.
        """
        self.log = get_task_logger()
        self.max_workers = max_workers or max(1, mp.cpu_count() - 1)
        self.pool: Optional[Pool] = None
        self.jobs: Dict[str, JobRecord] = {}  # job_id → metadata

    # ------------------------------
    # Internal pool management
    # ------------------------------
    def _ensure_pool(self):
        if self.pool is None:
            self.pool = mp.Pool(self.max_workers)
            self.log.info(f"WorkerPool created with {self.max_workers} workers")

    # ------------------------------
    # Submit a job (Dispatcher calls this)
    # ------------------------------
    def submit_job(self, job: JobRecord):
        self._ensure_pool()
        self.jobs[job.job_id] = job
        job.status = JobStatus.RUNNING

        # Apply async
        self.pool.apply_async(
            worker_entry,
            args=(job.job_id, job.files, job.config),
            callback=lambda res: self._job_success(job.job_id, res),
            error_callback=lambda err: self._job_error(job.job_id, err),
        )

        self.log.info(f"Job submitted to pool: {job.job_id}")

    # ------------------------------
    # Success callback
    # ------------------------------
    def _job_success(self, job_id: str, result: Any):
        job = self.jobs[job_id]
        job.status = JobStatus.FINISHED
        job.end_time = time.time()
        job.message = "Completed successfully"
        job.progress = {"done": True}

        self.log.info(f"[Job {job_id}] finished successfully")

    # ------------------------------
    # Error callback
    # ------------------------------
    def _job_error(self, job_id: str, err: Exception):
        job = self.jobs[job_id]
        job.status = JobStatus.ERROR
        job.end_time = time.time()
        job.message = str(err)
        job.errors.append(str(err))

        self.log.error(f"[Job {job_id}] ERROR: {err}")

    # ------------------------------
    # Cancel job (soft cancel)
    # ------------------------------
    def cancel_job(self, job_id: str):
        job = self.jobs.get(job_id)
        if not job:
            return

        job.status = JobStatus.CANCELLED
        job.end_time = time.time()
        job.message = "Cancelled by user"

        self.log.warning(f"[Job {job_id}] cancelled")

    # ------------------------------
    # Update job progress (called by worker)
    # ------------------------------
    def update_job_progress(self, job_id: str, progress: dict):
        job = self.jobs.get(job_id)
        if not job:
            return
        job.progress = progress

    # ------------------------------
    # Get Job
    # ------------------------------
    def get_job(self, job_id: str) -> Optional[JobRecord]:
        return self.jobs.get(job_id)

    # ------------------------------
    # Shutdown pool
    # ------------------------------
    def shutdown(self):
        if self.pool:
            self.pool.terminate()
            self.pool.join()
            self.pool = None
            self.log.info("WorkerPool shutdown")
