# 索引 /data 下文件并维护元信息
"""
FileIndexer — maintains listing and metadata of input data directory.

Features:
- list valid tar.gz files
- detect bank / rack types
- cache file metadata (size, mtime)
"""

import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from ..config import settings


class FileIndexer:

    def __init__(self, data_dir: str | None = None):
        self.data_dir = Path(data_dir or settings.DATA_DIR)
        self.cache: Dict[str, Dict] = {}

    # ------------------------------------------------------------
    # List tar.gz files under /data
    # ------------------------------------------------------------
    def list_tar_files(self) -> List[str]:
        self.refresh()
        return list(self.cache.keys())

    # ------------------------------------------------------------
    # Refresh file metadata
    # ------------------------------------------------------------
    def refresh(self):
        self.cache.clear()

        if not self.data_dir.exists():
            return

        for f in self.data_dir.glob("*.tar.gz"):
            stat = f.stat()
            self.cache[f.name] = {
                "path": str(f),
                "size_mb": round(stat.st_size / 1024 / 1024, 2),
                "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_bank": "bank" in f.name.lower(),
                "is_rack": "rack" in f.name.lower()
            }

    # ------------------------------------------------------------
    # Get metadata of a file
    # ------------------------------------------------------------
    def get_meta(self, filename: str) -> Dict:
        if filename not in self.cache:
            self.refresh()
        return self.cache.get(filename, {})
