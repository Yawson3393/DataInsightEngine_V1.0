"""
Worker side process: runs inside multiprocessing worker
"""

import tarfile
import io
from pathlib import Path
import time
import traceback
from typing import List, Dict, Any

from ..logging_cfg import get_task_logger
from .resource_ctl import ResourceGuard

# Parsers
from ..parsers.summary_parser import parse_summary_csv
from ..parsers.batvol_parser import parse_batvol_csv
from ..parsers.battemp_parser import parse_battemp_csv

# Aligner
from ..aligner.timeline_aligner import align_day_data

# Analysis
from ..analysis.compute_features import compute_battery_features

# Result storage
from ..storage.result_store import ResultStore

# Job status enum
from .status import JobStatus


def worker_entry(job_id: str, files: List[str], config: Dict[str, Any]):
    """
    Worker 子进程的实际执行入口
    """
    log = get_task_logger(job_id)
    t0 = time.time()

    # 必须创建 ResourceGuard(job_id)
    guard = ResourceGuard(job_id)
    log.info(f"[Worker] Start job {job_id}")

    # 存储原始数据
    day_raw = {"summary": {}, "rack": {}}

    try:
        # =========================
        # INGEST PHASE
        # =========================
        for tar_path in files:
            tar_path = Path(tar_path)

            if not tar_path.exists():
                log.warning(f"Missing file {tar_path}")
                continue

            with tarfile.open(tar_path, "r:gz") as tf:
                for member in tf.getmembers():
                    if not member.isfile():
                        continue

                    name = member.name.lower()
                    raw_bytes = tf.extractfile(member).read()

                    if "summary" in name:
                        data = parse_summary_csv(io.BytesIO(raw_bytes))
                        _merge_summary(day_raw, data, name)

                    elif "batvol" in name:
                        data = parse_batvol_csv(io.BytesIO(raw_bytes))
                        _merge_batvol(day_raw, data, name)

                    elif "battemp" in name:
                        data = parse_battemp_csv(io.BytesIO(raw_bytes))
                        _merge_battemp(day_raw, data, name)

                    guard.check_rss()  # 内存监控

        # =========================
        # ALIGN PHASE
        # =========================
        aligned = align_day_data(day_raw, config)
        guard.check_rss()

        # =========================
        # ANALYSIS PHASE
        # =========================
        features = compute_battery_features(aligned, config)

        # =========================
        # SAVE PHASE
        # =========================
        store = ResultStore()
        store.save_job_result(job_id, aligned, features)

        return {
            "job_id": job_id,
            "status": JobStatus.FINISHED,
            "duration": round(time.time() - t0, 2)
        }

    except Exception as e:
        log.error(f"Worker error: {e}\n{traceback.format_exc()}")
        return {
            "job_id": job_id,
            "status": JobStatus.ERROR,
            "message": str(e),
            "traceback": traceback.format_exc()
        }


# =====================================
# Internal helpers
# =====================================

def _merge_summary(day_raw, data, fname):
    if "bank" in fname:
        day_raw["summary"]["bank"] = data
    elif "rack" in fname:
        rack_id = _extract_rack_id(fname)
        day_raw["rack"].setdefault(rack_id, {})["summary"] = data


def _merge_batvol(day_raw, data, fname):
    rack_id = _extract_rack_id(fname)
    day_raw["rack"].setdefault(rack_id, {})["batvol"] = data


def _merge_battemp(day_raw, data, fname):
    rack_id = _extract_rack_id(fname)
    day_raw["rack"].setdefault(rack_id, {})["battemp"] = data


def _extract_rack_id(fname: str):
    fname = fname.lower()
    if "rack" not in fname:
        return "unknown"
    digits = ""
    for c in fname[fname.index("rack") + 4:]:
        if c.isdigit():
            digits += c
        else:
            break
    return f"rack{digits}"
