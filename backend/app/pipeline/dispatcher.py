# 任务分割、stage 管理（ingest→align→analyze）
# 任务分割 + 阶段控制（ingest → align → analyze → store）
"""
dispatcher.py
-------------
Coordinates multi-stage processing pipeline:
1. ingest  (tar.gz → file streams → CSV chunks)
2. parse   (CSV → DataFrame/Chunk)
3. align   (resample to unified timeline)
4. analyze (plugins)
5. store   (Parquet / cache / metadata)

The dispatcher:
- Accepts a task_id and list of tar files
- Splits them into work units
- Pushes work units into worker_pool
- Pushes progress updates
"""

import uuid
from loguru import logger
from multiprocessing import Queue
from pathlib import Path

from .worker_pool import WorkerPool
from .resource_ctl import ResourceController
from ..tasks.progress import progress_manager
from ..config import settings
from ..ingest.tar_stream import stream_tar_members


class Dispatcher:
    """
    Orchestrates the multi-process pipeline.

    Responsibilities:
    - Create work units (tar_member jobs)
    - Push jobs to worker pool
    - Drain worker results
    - Update progress
    """

    def __init__(self):
        self.worker_pool = WorkerPool(
            n_workers=settings.MAX_WORKERS,
            queue_size=settings.WORKER_QUEUE_SIZE
        )
        self.resource_ctl = ResourceController()

    def start_task(self, task_id: str, tar_files: list[str]):
        logger.info(f"[Dispatcher] Starting task={task_id}")
        progress_manager.push(task_id, msg="Task started", stage="init")

        # Build job list
        jobs = []
        for tar in tar_files:
            full_path = settings.DATA_ROOT / tar
            if not full_path.exists():
                logger.error(f"File not found: {full_path}")
                continue

            for member_name, _ in stream_tar_members(full_path):
                job_id = str(uuid.uuid4())
                jobs.append({
                    "task_id": task_id,
                    "job_id": job_id,
                    "tar_file": tar,
                    "member": member_name,
                })

        if not jobs:
            progress_manager.push(task_id, msg="No valid jobs found", stage="error")
            return

        total = len(jobs)
        logger.info(f"[Dispatcher] Created {total} jobs for task={task_id}")

        progress_manager.set_total(task_id, total)

        # Enqueue jobs
        for job in jobs:
            self.worker_pool.submit(job)

        # Drain results
        completed = 0
        for result in self.worker_pool.results():
            completed += 1
            progress_manager.update(
                task_id,
                finished=completed,
                msg=f"Completed {completed}/{total}",
                stage=result.get("stage", "done")
            )

        progress_manager.push(task_id, msg="Task finished", stage="complete")
        logger.info(f"[Dispatcher] Task finished: {task_id}")


# Global dispatcher instance
dispatcher = Dispatcher()
