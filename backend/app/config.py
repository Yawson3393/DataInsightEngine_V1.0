# backend/app/config.py
from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    DATA_ROOT: str = os.getenv("DATA_ROOT", "data")
    OUTPUT_ROOT: str = os.getenv("OUTPUT_ROOT", "storage")
    CHUNK_ROWS: int = int(os.getenv("CHUNK_ROWS", "5000"))
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    MODULE_CELLS: int = int(os.getenv("MODULE_CELLS", "32"))
    MODULE_ROWS: int = int(os.getenv("MODULE_ROWS", "4"))
    MODULE_COLS: int = int(os.getenv("MODULE_COLS", "8"))
    TEMP_SENSORS_PER_MODULE: int = int(os.getenv("TEMP_SENSORS_PER_MODULE","20"))
    TIME_FORMAT: str = os.getenv("TIME_FORMAT", "%Y/%m/%d %H:%M:%S")
    PARQUET_ENABLED: bool = os.getenv("PARQUET_ENABLED","1") == "1"

settings = Settings()
