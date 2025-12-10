import sys
import json
from pathlib import Path
from loguru import logger

from .config import settings


# ----------------------------------------------------------
# JSON formatter wrapper (sink handler)
# ----------------------------------------------------------
def json_sink(message):
    record = message.record

    log = {
        "time": record["time"].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
        "process": record["process"].id,
        "thread": record["thread"].id,
    }

    # extra fields
    if record["extra"]:
        log.update(record["extra"])

    # exception
    if record["exception"]:
        log["exception"] = str(record["exception"])

    # write JSON line
    with open(settings.LOG_DIR / "structured.jsonl", "a", encoding="utf8") as f:
        f.write(json.dumps(log) + "\n")


# ----------------------------------------------------------
# Human-friendly text formatter (sink)
# ----------------------------------------------------------
def human_sink(message):
    record = message.record
    ts = record["time"].strftime("%Y-%m-%d %H:%M:%S")
    line = (
        f"{ts} | {record['level'].name:<8} | "
        f"{record['module']}.{record['function']}:{record['line']} - "
        f"{record['message']}\n"
    )
    sys.stdout.write(line)


# ----------------------------------------------------------
# Setup logging
# ----------------------------------------------------------
def setup_logging():
    logger.remove()

    logs_dir = settings.LOG_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)

    # console
    logger.add(
        human_sink,
        level="INFO",
        enqueue=True,
    )

    # file (human)
    logger.add(
        logs_dir / "core.log",
        level="INFO",
        rotation="20 MB",
        retention=5,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        enqueue=True,
    )

    # JSON sink
    logger.add(
        json_sink,
        level="INFO",
        enqueue=True,
    )

    logger.info("Logging system initialized.")


def get_task_logger(task_id=None, job_id=None):
    extra = {}
    if task_id:
        extra["task_id"] = task_id
    if job_id:
        extra["job_id"] = job_id
    return logger.bind(**extra)
