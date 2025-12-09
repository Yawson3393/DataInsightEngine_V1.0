# backend/app/api/files.py
import os
from fastapi import APIRouter
from ..config import settings

router = APIRouter()

@router.get("/list")
def list_files():
    folder = settings.DATA_ROOT
    files = []
    if os.path.isdir(folder):
        for name in sorted(os.listdir(folder)):
            if name.endswith(".tar.gz"):
                path = os.path.join(folder, name)
                files.append({
                    "filename": name,
                    "size": os.path.getsize(path)
                })
    return {"files": files}
