"""
Job Model (in-memory representation)
"""
from enum import Enum
from typing import List, Optional
from datetime import datetime


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class JobStage(str, Enum):
    INGEST = "INGEST"
    ALIGN = "ALIGN"
    ANALYZE = "ANALYZE"
    EXPORT = "EXPORT"   # 预留（生成报告）


class Job:
    def __init__(
        self,
        job_id: str,
        files: List[str],
        status: JobStatus = JobStatus.PENDING,
        stage: Optional[JobStage] = None,
        created_at: Optional[datetime] = None,
        started_at: Optional[datetime] = None,
        ended_at: Optional[datetime] = None,
        error: Optional[str] = None,
    ):
        self.job_id = job_id
        self.files = files
        self.status = status
        self.stage = stage or JobStage.INGEST
        self.created_at = created_at or datetime.utcnow()
        self.started_at = started_at
        self.ended_at = ended_at
        self.error = error

    # convenience for dict conversion (JSON for API)
    def to_dict(self):
        return {
            "job_id": self.job_id,
            "files": self.files,
            "status": self.status.value,
            "stage": self.stage.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "error": self.error,
        }
