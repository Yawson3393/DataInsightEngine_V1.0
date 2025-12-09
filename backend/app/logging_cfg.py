# loguru / structured logging 配置

"""
logging_cfg.py
---------------
Centralized logging system using Loguru.
Supports:
- Structured JSON logging (optional)
- File + console output
- Log rotation
- Integration with multiprocessing (worker logs)
- Enrich log messages with task/job context
"""

import sys
import json
from pathlib import Path
from loguru import logger
from datetime import datetime

from .config import settings


# ----------------------------------------------------------
# Custom JSON formatter for structured logs
# ----------------------------------------------------------
def json_formatter(record):
    """Structured JSON log format."""
    log = {
        "timestamp": record["time"].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
        "process": record["process"].id,
        "thread": record["thread"].id,
    }

    # Support context variables for task/job
    if "extra" in record:
        log.update(record["extra"])

    # Exception info (if exists)
    if record["exception"]:
        log["exception"] = str(record["exception"])

    return json.dumps(log)


# ----------------------------------------------------------
# Non-JSON console formatter
# ----------------------------------------------------------
def human_formatter(record):
    ts = record["time"].strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"{ts} | {record['level'].name:<8} | "
        f"{record['module']}.{record['function']}:{record['line']} - "
        f"{record['message']}"
    )


# ----------------------------------------------------------
# Setup Logging
# ----------------------------------------------------------
def setup_logging():
    """
    Configure loguru for the entire project.
    - Remove default handler
    - Add console + file sink
    - Enable rotation & retention
    - Support JSON logs (optional switch)
    """

    logger.remove()

    logs_dir = settings.LOG_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Console logging
    # -------------------------
    logger.add(
        sys.stdout,
        level="INFO",
        format=human_formatter,
        enqueue=True,               # works across multiprocessing
        backtrace=False,
        diagnose=False,
    )

    # -------------------------
    # File logging (human-readable)
    # -------------------------
    logger.add(
        logs_dir / "app.log",
        rotation="20 MB",
        retention=5,
        level="INFO",
        format=human_formatter,
        enqueue=True,
    )

    # -------------------------
    # JSON structured logs
    # -------------------------
    logger.add(
        logs_dir / "structured.jsonl",
        rotation="50 MB",
        retention="7 days",
        serialize=False,
        level="INFO",
        format=json_formatter,
        backtrace=False,
        diagnose=False,
        enqueue=True,
    )

    logger.info("Logging system initialized.")


# ----------------------------------------------------------
# Helpers for task/job log enrichment
# ----------------------------------------------------------
def get_task_logger(task_id=None, job_id=None):
    """
    Create a logger bound to specific task_id or job_id.
    Example:
        log = get_task_logger(task_id="123")
        log.info("Parsing rack1")
    """
    extra = {}
    if task_id:
        extra["task_id"] = task_id
    if job_id:
        extra["job_id"] = job_id

    return logger.bind(**extra)
