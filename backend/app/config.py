"""
Global Configuration Module

Supports:
- Centralized system parameters
- Environment variable override
- Physical mapping: heap → rack → module → cell
- Streaming settings (chunk size, memory limits)
- Worker configuration
- Optional frontend hosting
"""

from pathlib import Path
from typing import List
from pydantic import BaseSettings


class Settings(BaseSettings):
    # ----------------------------------------------
    # Project folders
    # ----------------------------------------------
    DATA_ROOT: Path = Path("/data")                 # where tar.gz files are stored
    OUTPUT_ROOT: Path = Path("/storage")            # where parquet & results are saved

    LOG_DIR: Path = Path("logs")

    # ----------------------------------------------
    # Server settings
    # ----------------------------------------------
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ALLOW_ORIGINS: List[str] = ["*"]

    # ----------------------------------------------
    # Streaming config (memory-safe)
    # ----------------------------------------------
    CHUNK_ROWS: int = 5000                     # rows per CSV chunk
    READ_BUFFER_SIZE: int = 4 * 1024 * 1024    # 4MB streaming buffer

    MEMORY_SOFT_LIMIT_MB: int = 200            # max worker memory
    MEMORY_HARD_LIMIT_MB: int = 300            # kill worker if exceeded

    # ----------------------------------------------
    # Worker settings
    # ----------------------------------------------
    MAX_WORKERS: int = 4                       # CPU parallel workers
    WORKER_QUEUE_SIZE: int = 32                # backpressure control

    # ----------------------------------------------
    # Time alignment
    # ----------------------------------------------
    TIME_GRID: str = "5S"                      # align to 5-second intervals

    # ----------------------------------------------
    # Battery physical hierarchy (CR Liyujiang example)
    # ----------------------------------------------
    HEAPS_PER_UNIT: int = 4
    RACKS_PER_HEAP: int = 2
    MODULES_PER_RACK: int = 7

    MODULE_ROWS: int = 4         # 4 rows × 8 columns = 32 cells
    MODULE_COLS: int = 8
    MODULE_CELLS: int = 32

    TEMP_SENSORS_PER_MODULE: int = 20

    # ----------------------------------------------
    # Scaling factors
    # ----------------------------------------------
    VOLTAGE_SCALE_SUMMARY: float = 0.1
    VOLTAGE_SCALE_RACK: float = 0.1
    VOLTAGE_SCALE_CELL: float = 0.001

    TEMP_SCALE_CELL: float = 0.1

    # ----------------------------------------------
    # Thresholds (default values)
    # ----------------------------------------------
    CHARGE_VOLTAGE_LIMIT: float = 3650
    DISCHARGE_VOLTAGE_LIMIT: float = 2800
    NOMINAL_CELL_VOLTAGE: float = 3200
    MAX_TEMP_DIFF: float = 2.0

    # ----------------------------------------------
    # Parquet storage settings
    # ----------------------------------------------
    PARQUET_COMPRESSION: str = "snappy"
    PARQUET_ROW_GROUP_SIZE: int = 50000

    # ----------------------------------------------
    # Frontend hosting (optional)
    # ----------------------------------------------
    SERVE_FRONTEND: bool = False
    FRONTEND_DIST: Path = Path("frontend/dist")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# global settings instance
settings = Settings()
