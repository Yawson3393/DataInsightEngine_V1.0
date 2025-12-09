# backend/app/api/analysis.py
from fastapi import APIRouter, HTTPException
from ..storage.parquet_store import ParquetStore

router = APIRouter()

@router.get("/overview/{task_id}")
def overview(task_id: str):
    store = ParquetStore(task_id)
    try:
        return store.load_overview()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="results not found")

@router.get("/download/{task_id}")
def download_zip(task_id: str):
    store = ParquetStore(task_id)
    return store.get_zip_path()
