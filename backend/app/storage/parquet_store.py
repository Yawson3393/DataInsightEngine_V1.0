"""
Parquet Store: columnar storage for battery data
Uses Polars for fast IO.
"""

import os
from pathlib import Path
import polars as pl
from typing import Dict, List, Any
import threading

_WRITE_LOCK = threading.Lock()


class ParquetStore:
    """
    Manage parquet storage for:
    - stack summary
    - rack summary
    - cell voltage
    - cell temperature

    Directory layout:
        storage_root/
            stack_{stack_id}/
                summary.parquet
            rack_{rack_id}/
                summary.parquet
                batvol.parquet
                battemp.parquet
    """

    def __init__(self, root: str = "./storage_data"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------
    def _path(self, parts: List[str]) -> Path:
        p = self.root.joinpath(*parts)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------

    def write_stack_summary(self, stack_id: int, df: pl.DataFrame):
        """
        Write stack-level summary (append mode).
        """
        path = self._path([f"stack_{stack_id}", "summary.parquet"])
        with _WRITE_LOCK:
            if path.exists():
                old = pl.read_parquet(path)
                df = pl.concat([old, df], how="vertical_relaxed")
            df.write_parquet(path)

    def write_rack_summary(self, rack_id: int, df: pl.DataFrame):
        path = self._path([f"rack_{rack_id}", "summary.parquet"])
        with _WRITE_LOCK:
            if path.exists():
                old = pl.read_parquet(path)
                df = pl.concat([old, df], how="vertical_relaxed")
            df.write_parquet(path)

    def write_batvol(self, rack_id: int, df: pl.DataFrame):
        path = self._path([f"rack_{rack_id}", "batvol.parquet"])
        with _WRITE_LOCK:
            if path.exists():
                old = pl.read_parquet(path)
                df = pl.concat([old, df], how="vertical_relaxed")
            df.write_parquet(path)

    def write_battemp(self, rack_id: int, df: pl.DataFrame):
        path = self._path([f"rack_{rack_id}", "battemp.parquet"])
        with _WRITE_LOCK:
            if path.exists():
                old = pl.read_parquet(path)
                df = pl.concat([old, df], how="vertical_relaxed")
            df.write_parquet(path)

    # ------------------------------------------------------------
    # Read methods
    # ------------------------------------------------------------

    def read_stack_summary(self, stack_id: int) -> pl.DataFrame:
        path = self._path([f"stack_{stack_id}", "summary.parquet"])
        if not path.exists():
            return pl.DataFrame()
        return pl.read_parquet(path)

    def read_rack_summary(self, rack_id: int) -> pl.DataFrame:
        path = self._path([f"rack_{rack_id}", "summary.parquet"])
        if not path.exists():
            return pl.DataFrame()
        return pl.read_parquet(path)

    def read_batvol(self, rack_id: int) -> pl.DataFrame:
        path = self._path([f"rack_{rack_id}", "batvol.parquet"])
        if not path.exists():
            return pl.DataFrame()
        return pl.read_parquet(path)

    def read_battemp(self, rack_id: int) -> pl.DataFrame:
        path = self._path([f"rack_{rack_id}", "battemp.parquet"])
        if not path.exists():
            return pl.DataFrame()
        return pl.read_parquet(path)

    # ------------------------------------------------------------
    # Delete / Cleanup
    # ------------------------------------------------------------

    def clear_rack(self, rack_id: int):
        path = self.root / f"rack_{rack_id}"
        if path.exists():
            for f in path.glob("*.parquet"):
                f.unlink()

    def clear_stack(self, stack_id: int):
        path = self.root / f"stack_{stack_id}"
        if path.exists():
            for f in path.glob("*.parquet"):
                f.unlink()
