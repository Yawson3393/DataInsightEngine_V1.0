import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from ..config import settings

router = APIRouter()


class FileMeta(BaseModel):
    name: str
    size_mb: float
    modified: str
    path: str


@router.get("/", response_model=List[FileMeta])
def list_data_files():
    """
    Return all tar.gz files under /data directory.
    (bank_ / rack_ files)
    """
    data_dir = Path(settings.DATA_DIR)
    if not data_dir.exists():
        raise HTTPException(404, f"Data directory not found: {data_dir}")

    files = []

    for f in data_dir.glob("*.tar.gz"):
        stat = f.stat()
        files.append(
            FileMeta(
                name=f.name,
                size_mb=round(stat.st_size / 1024 / 1024, 2),
                modified=str(datetime.fromtimestamp(stat.st_mtime)),
                path=str(f),
            )
        )

    return files


@router.get("/{filename}", response_model=FileMeta)
def file_metadata(filename: str):
    fpath = Path(settings.DATA_DIR) / filename
    if not fpath.exists():
        raise HTTPException(404, f"File not found: {filename}")

    stat = fpath.stat()

    return FileMeta(
        name=fpath.name,
        size_mb=round(stat.st_size / 1024 / 1024, 2),
        modified=str(datetime.fromtimestamp(stat.st_mtime)),
        path=str(fpath),
    )
