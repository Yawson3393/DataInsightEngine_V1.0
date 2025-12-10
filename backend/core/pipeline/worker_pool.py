import multiprocessing as mp
from multiprocessing.pool import Pool
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Any

from ..logging_cfg import get_task_logger
from .status import JobStatus    # ⭐ FIX：从 status.py 引入

# ⭐ FIX：延迟 import，避免 circular import
# from .worker_process import worker_entry
def _load_worker_entry():
    from .worker_process import worker_entry
    return worker_entry


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


class WorkerPool:
    """Manages multiprocessing pool"""

    def __init__(self, max_workers: int = None):
        self.log = get_task_logger()
        self.max_workers = max_workers or max(1, mp.cpu_count() - 1)
        self.pool: Optional[Pool] = None
        self.jobs: Dict[str, JobRecord] = {}

    def _ensure_pool(self):
        if self.pool is None:
            self.pool = mp.Pool(self.max_workers)
            self.log.info(f"WorkerPool created with {self.max_workers} workers")

    def submit_job(self, job: JobRecord):
        self._ensure_pool()
        self.jobs[job.job_id] = job
        job.status = JobStatus.RUNNING

        worker_entry = _load_worker_entry()   # ⭐ FIX：避免循环 import

        self.pool.apply_async(
            worker_entry,
            args=(job.job_id, job.files, job.config),
            callback=lambda res: self._job_success(job.job_id, res),
            error_callback=lambda err: self._job_error(job.job_id, err),
        )
        self.log.info(f"Job submitted: {job.job_id}")

    def _job_success(self, job_id: str, result: dict):
        job = self.jobs[job_id]
        job.status = JobStatus.FINISHED
        job.end_time = time.time()
        job.progress = {"done": True}
        job.message = "Completed"

    def _job_error(self, job_id: str, err: Exception):
        job = self.jobs[job_id]
        job.status = JobStatus.ERROR
        job.end_time = time.time()
        job.message = str(err)
        job.errors.append(str(err))

    def get_job(self, job_id: str):
        return self.jobs.get(job_id)

    def shutdown(self):
        if self.pool:
            self.pool.terminate()
            self.pool.join()
            self.pool = None
