"""
Resource monitoring for worker processes.
Main class: ResourceGuard

Used to control:
- RSS memory (resident memory)
- CPU usage (optional)
- Trigger cleanup or fail-safe actions

This runs inside a worker process.
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
        on_limit_action: str = "gc",   # gc / warn / raise
    ):
        """
        Parameters
        ----------
        job_id : str
            job identifier for logging
        max_rss_gb : float
            RSS memory threshold (in GB)
        check_interval_sec : float
            minimum interval between rss checks
        on_limit_action : str
            behavior when hitting limit: gc / warn / raise
        """
        self.job_id = job_id
        self.max_rss = max_rss_gb * 1024**3  # convert GB → bytes
        self.check_interval = check_interval_sec
        self.on_limit_action = on_limit_action

        self.log = get_task_logger(job_id)
        self._last_check_time = 0
        self.process = psutil.Process(os.getpid())

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------
    def check_rss(self):
        """
        Check RSS usage of current worker.
        If exceeding threshold, execute action.
        """
        now = time.time()
        if now - self._last_check_time < self.check_interval:
            return

        self._last_check_time = now

        rss = self.process.memory_info().rss

        if rss < self.max_rss:
            self.log.debug(f"[ResourceGuard] RSS OK: {rss/1e6:.1f} MB")
            return

        # Exceed
        self.log.warning(
            f"[ResourceGuard] RSS too high! "
            f"{rss/1e9:.2f} GB > limit {self.max_rss/1e9:.2f} GB"
        )

        # Take action
        if self.on_limit_action == "gc":
            self._trigger_gc()

        elif self.on_limit_action == "warn":
            return

        elif self.on_limit_action == "raise":
            raise MemoryError(
                f"Worker memory exceeded: {rss/1e9:.2f} GB (limit {self.max_rss/1e9:.2f} GB)"
            )

    # ----------------------------------------------------------
    # Internal GC cleanup
    # ----------------------------------------------------------
    def _trigger_gc(self):
        """
        Force a full garbage collection cycle.
        """
        self.log.info("[ResourceGuard] Triggering GC cleanup...")
        gc.collect()
        rss_after = self.process.memory_info().rss
        self.log.info(
            f"[ResourceGuard] GC completed. "
            f"RSS now {rss_after/1e6:.1f} MB"
        )
