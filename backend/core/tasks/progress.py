"""
Progress model + WebSocket progress manager
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from fastapi import WebSocket
import asyncio


# ---------------------------------------------------------
# Data model used by workers
# ---------------------------------------------------------
@dataclass
class ProgressUpdate:
    job_id: str
    stage: str          # INGEST / ALIGN / ANALYZE
    percent: float      # 0 - 100
    detail: str         # message (e.g. "Parsing rack1 batVol")
    error: Optional[str] = None

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "stage": self.stage,
            "percent": self.percent,
            "detail": self.detail,
            "error": self.error,
        }


# ---------------------------------------------------------
# WebSocket manager used by main.py
# ---------------------------------------------------------
class ProgressManager:
    """
    Maintain WebSocket subscribers per task, and push progress messages.
    """

    def __init__(self):
        # task_id -> list of WebSocket
        self._subs: Dict[str, List[WebSocket]] = {}
        self._lock = asyncio.Lock()

    # subscribe
    async def connect(self, task_id: str, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._subs.setdefault(task_id, []).append(ws)

    # unsubscribe
    async def disconnect(self, task_id: str, ws: WebSocket):
        async with self._lock:
            if task_id in self._subs:
                self._subs[task_id] = [
                    c for c in self._subs[task_id] if c != ws
                ]

    # push update to all clients
    async def push(self, task_id: str, update: ProgressUpdate):
        if task_id not in self._subs:
            return

        payload = update.to_dict()
        dead = []

        for ws in self._subs[task_id]:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)

        # cleanup dead websockets
        for ws in dead:
            await self.disconnect(task_id, ws)


# ---------------------------------------------------------
# Global instance (this is what main.py expects)
# ---------------------------------------------------------
progress_manager = ProgressManager()

__all__ = ["ProgressUpdate", "ProgressManager", "progress_manager"]
