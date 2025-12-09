from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import Dict

from ..storage.result_store import ResultStore
from ..config import settings

router = APIRouter()
store = ResultStore(settings.RESULT_DIR)


@router.get("/{job_id}/overview", response_model=Dict)
def get_overview(job_id: str):
    """
    返回结构化分析摘要（堆 / 簇 / 模组 / 单体统计）
    数据示例:
      {
        "bank": {...},
        "rack1": {...},
        "rack2": {...},
        ...
      }
    """
    if not store.has_result(job_id):
        raise HTTPException(404, f"No results for job {job_id}")

    return store.load_overview(job_id)


@router.get("/{job_id}/download")
def download_result(job_id: str):
    """
    直接下载最终报告 ZIP 或 JSON。
    """
    f = store.get_bundle(job_id)
    if f is None or not Path(f).exists():
        raise HTTPException(404, f"No downloadable bundle for job {job_id}")

    return FileResponse(f, media_type="application/zip", filename=f"{job_id}.zip")
