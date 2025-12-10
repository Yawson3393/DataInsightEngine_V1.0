"""
Resource monitoring for worker processes.
Main class: ResourceGuard
"""

import psutil
import os
import gc
import time

from ..logging_cfg import get_task_logger


class ResourceGuard:
    """
    Monitor worker resource usage:
      - RSS memory
      - CPU (optional)
    """

    def __init__(
        self,
        job_id: str,
        max_rss_gb: float = 1.5,
        check_interval_sec: float = 3.0,
        on_limit_action: str = "gc",
    ):
        self.job_id = job_id
        self.max_rss = max_rss_gb * 1024**3
        self.check_interval = check_interval_sec
        self.on_limit_action = on_limit_action

        self.log = get_task_logger(job_id)
        self._last_check_time = 0
        self.process = psutil.Process(os.getpid())

    def check_rss(self):
        """Check RSS usage"""
        now = time.time()
        if now - self._last_check_time < self.check_interval:
            return

        self._last_check_time = now
        rss = self.process.memory_info().rss

        if rss < self.max_rss:
            return

        self.log.warning(
            f"[ResourceGuard] RSS too high: {rss/1e9:.2f} GB "
            f"(limit {self.max_rss/1e9:.2f} GB)"
        )

        if self.on_limit_action == "gc":
            self._trigger_gc()
        elif self.on_limit_action == "raise":
            raise MemoryError("Worker exceeded memory limit")

    def _trigger_gc(self):
        self.log.info("[ResourceGuard] Triggering GC...")
        gc.collect()
