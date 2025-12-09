"""
Task Manager:
- store job metadata in sqlite
- update status/stage/progress
- used by Jobs API, dispatcher, workers
"""

import sqlite3
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .job import Job, JobStatus, JobStage


DB_FILE = "./task_meta.sqlite"
_LOCK = threading.Lock()


def _conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def init_db():
    conn = _conn()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            files_json TEXT,
            status TEXT,
            stage TEXT,
            created_at TEXT,
            started_at TEXT,
            ended_at TEXT,
            error TEXT
        );
        """
    )
    conn.commit()
    conn.close()


# ensure DB exists
init_db()


class TaskManager:
    """
    Manage job metadata with sqlite (thread-safe)
    """

    @staticmethod
    def create_job(job_id: str, files: List[str]) -> Job:
        with _LOCK:
            conn = _conn()
            cur = conn.cursor()

            created_at = datetime.utcnow().isoformat()

            cur.execute(
                """
                INSERT INTO jobs (job_id, files_json, status, stage, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    json.dumps(files),
                    JobStatus.PENDING.value,
                    JobStage.INGEST.value,
                    created_at,
                ),
            )
            conn.commit()
            conn.close()

        return Job(job_id, files)

    @staticmethod
    def get_job(job_id: str) -> Optional[Job]:
        conn = _conn()
        cur = conn.cursor()

        cur.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        (
            job_id,
            files_json,
            status,
            stage,
            created_at,
            started_at,
            ended_at,
            error,
        ) = row

        return Job(
            job_id=job_id,
            files=json.loads(files_json),
            status=JobStatus(status),
            stage=JobStage(stage),
            created_at=datetime.fromisoformat(created_at),
            started_at=datetime.fromisoformat(started_at) if started_at else None,
            ended_at=datetime.fromisoformat(ended_at) if ended_at else None,
            error=error,
        )

    @staticmethod
    def update_status(job_id: str, status: JobStatus):
        with _LOCK:
            conn = _conn()
            cur = conn.cursor()

            t = datetime.utcnow().isoformat()
            if status == JobStatus.RUNNING:
                cur.execute(
                    "UPDATE jobs SET status=?, started_at=? WHERE job_id=?",
                    (status.value, t, job_id),
                )
            elif status in (JobStatus.SUCCESS, JobStatus.FAILED, JobStatus.CANCELLED):
                cur.execute(
                    "UPDATE jobs SET status=?, ended_at=? WHERE job_id=?",
                    (status.value, t, job_id),
                )
            conn.commit()
            conn.close()

    @staticmethod
    def update_stage(job_id: str, stage: JobStage):
        with _LOCK:
            conn = _conn()
            cur = conn.cursor()
            cur.execute(
                "UPDATE jobs SET stage=? WHERE job_id=?",
                (stage.value, job_id),
            )
            conn.commit()
            conn.close()

    @staticmethod
    def set_error(job_id: str, error_msg: str):
        with _LOCK:
            conn = _conn()
            cur = conn.cursor()
            cur.execute(
                "UPDATE jobs SET error=?, status=?, ended_at=? WHERE job_id=?",
                (
                    error_msg,
                    JobStatus.FAILED.value,
                    datetime.utcnow().isoformat(),
                    job_id,
                ),
            )
            conn.commit()
            conn.close()

    @staticmethod
    def list_jobs() -> List[Job]:
        conn = _conn()
        cur = conn.cursor()

        cur.execute("SELECT job_id FROM jobs ORDER BY created_at DESC")
        ids = [row[0] for row in cur.fetchall()]
        conn.close()

        return [TaskManager.get_job(j) for j in ids]
