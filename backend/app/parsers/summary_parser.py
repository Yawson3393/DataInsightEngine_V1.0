# backend/app/parsers/summary_parser.py
import pandas as pd
from typing import Dict, Any
from ..config import settings

def parse(fileobj, chunksize=None):
    """
    Parse summary CSV stream and yield cleaned chunks as DataFrame
    """
    # fileobj is binary file-like from tar.extractfile
    txt = fileobj
    # pandas will accept binary, but we wrap to text if necessary
    try:
        df_iter = pd.read_csv(txt, chunksize=settings.CHUNK_ROWS)
    except Exception:
        txt.seek(0)
        df_iter = pd.read_csv(txt, chunksize=settings.CHUNK_ROWS)
    for chunk in df_iter:
        # basic clean: strip column names
        chunk.columns = [c.strip() for c in chunk.columns]
        # convert time column
        if 'time' in chunk.columns:
            chunk['time'] = pd.to_datetime(chunk['time'].astype(str).str.strip(), format=settings.TIME_FORMAT, errors='coerce')
        yield chunk
