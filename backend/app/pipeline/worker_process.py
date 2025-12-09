"""
Worker side process:
Each worker handles exactly one job (one set of tar.gz input files).

The central entry function is worker_entry(job_id, files, config),
which is called from worker_pool.apply_async().
"""

import tarfile
import io
from pathlib import Path
from typing import List, Dict, Any
import traceback
import time

from ..logging_cfg import get_task_logger
from .resource_ctl import ResourceGuard

# Parsers:
from ..parsers.summary_parser import parse_summary_csv
from ..parsers.batvol_parser import parse_batvol_csv
from ..parsers.battemp_parser import parse_battemp_csv

# Stages:
from ..analysis.aligner import align_day_data
from ..analysis.compute_features import compute_battery_features

# Storage:
from ..storage.result_store import ResultStore

from .worker_pool import JobStatus  # for status enum


# ----------------------------
# Worker entry point
# ----------------------------
def worker_entry(job_id: str, files: List[str], config: Dict[str, Any]):
    """
    Main entry executed inside a worker process.
    This function MUST return a Python object (callback result).
    """

    log = get_task_logger(job_id)
    log.info(f"[Worker] Started job {job_id}")
    t0 = time.time()

    # safety guard: memory & CPU tracking
    guard = ResourceGuard(job_id)

    result_store = ResultStore()

    # Output structure
    day_raw = {
        "summary": {},
        "rack": {},       # each rack: summary, batvol, battemp
    }

    try:
        # ---------------------------------------------------------
        # Stage 1: INGEST (streaming tar.gz without extraction)
        # ---------------------------------------------------------
        log.info("[INGEST] Start ingesting tar.gz files")

        for tar_path in files:
            tar_path = Path(tar_path)
            if not tar_path.exists():
                log.warning(f"File not found, skip: {tar_path}")
                continue

            log.info(f"[INGEST] Open TAR: {tar_path}")

            with tarfile.open(tar_path, "r:gz") as tf:
                for member in tf.getmembers():
                    if not member.isfile():
                        continue

                    fname = member.name.lower()

                    # summary
                    if "summary" in fname:
                        file_bytes = tf.extractfile(member).read()
                        data = parse_summary_csv(io.BytesIO(file_bytes))
                        _merge_summary(day_raw, data, fname)
                        log.info(f"Parsed summary: {fname}")

                    # batVol
                    elif "batvol" in fname:
                        file_bytes = tf.extractfile(member).read()
                        data = parse_batvol_csv(io.BytesIO(file_bytes))
                        _merge_batvol(day_raw, data, fname)
                        log.info(f"Parsed batVol: {fname}")

                    # batTemp
                    elif "battemp" in fname:
                        file_bytes = tf.extractfile(member).read()
                        data = parse_battemp_csv(io.BytesIO(file_bytes))
                        _merge_battemp(day_raw, data, fname)
                        log.info(f"Parsed batTemp: {fname}")

                    guard.check_rss()   # ensure memory safe

        # Save intermediate raw if needed
        log.info("[INGEST] Completed")

        # ---------------------------------------------------------
        # Stage 2: ALIGN
        # ---------------------------------------------------------
        log.info("[ALIGN] Start aligning...")
        aligned = align_day_data(day_raw, config)
        log.info("[ALIGN] Completed")

        guard.check_rss()

        # ---------------------------------------------------------
        # Stage 3: ANALYSIS
        # ---------------------------------------------------------
        log.info("[ANALYZE] Start battery analytics...")

        features = compute_battery_features(aligned, config)

        log.info("[ANALYZE] Completed")

        # ---------------------------------------------------------
        # Save final result
        # ---------------------------------------------------------
        log.info("[SAVE] Store results")

        result_store.save_job_result(job_id, aligned, features)

        log.info(f"[Worker] Finished job {job_id} in {round(time.time()-t0,2)} sec")

        return {
            "job_id": job_id,
            "status": JobStatus.FINISHED,
            "message": "success",
            "duration": round(time.time() - t0, 3)
        }

    except Exception as e:
        log.error(f"[Worker] ERROR: {e}")
        log.error(traceback.format_exc())

        return {
            "job_id": job_id,
            "status": JobStatus.ERROR,
            "message": str(e),
            "traceback": traceback.format_exc()
        }


# ==========================================================
# Helpers for merging partial data
# ==========================================================

def _merge_summary(day_raw, data, fname):
    """
    summary CSV has:
      - bank0summary_ ...
      - rack1summary_ ...
    """
    fname = fname.lower()
    if "bank" in fname:
        day_raw["summary"]["bank"] = data
    elif "rack" in fname:
        # extract rack id
        rack_id = _extract_rack_id(fname)
        if rack_id not in day_raw["rack"]:
            day_raw["rack"][rack_id] = {}
        day_raw["rack"][rack_id]["summary"] = data


def _merge_batvol(day_raw, data, fname):
    rack_id = _extract_rack_id(fname.lower())
    if rack_id not in day_raw["rack"]:
        day_raw["rack"][rack_id] = {}
    day_raw["rack"][rack_id]["batvol"] = data


def _merge_battemp(day_raw, data, fname):
    rack_id = _extract_rack_id(fname.lower())
    if rack_id not in day_raw["rack"]:
        day_raw["rack"][rack_id] = {}
    day_raw["rack"][rack_id]["battemp"] = data


def _extract_rack_id(fname: str) -> str:
    # fname contains "rack1", "rack2", ...
    idx = fname.find("rack")
    if idx == -1:
        return "unknown"
    num_part = ""
    for ch in fname[idx+4:]:
        if ch.isdigit():
            num_part += ch
        else:
            break
    return f"rack{num_part}"
