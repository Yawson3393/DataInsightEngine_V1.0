# backend/app/parsers/battemp_parser.py
import pandas as pd
from ..config import settings

def parse(fileobj, chunksize=None):
    txt = fileobj
    try:
        it = pd.read_csv(txt, chunksize=settings.CHUNK_ROWS)
    except Exception:
        txt.seek(0)
        it = pd.read_csv(txt, chunksize=settings.CHUNK_ROWS)
    for chunk in it:
        chunk.columns = [c.strip() for c in chunk.columns]
        tcols = [c for c in chunk.columns if c.startswith('T')]
        for c in tcols:
            chunk[c] = pd.to_numeric(chunk[c], errors='coerce')
        if 'time' in chunk.columns:
            chunk['time'] = pd.to_datetime(chunk['time'].astype(str).str.strip(), format=settings.TIME_FORMAT, errors='coerce')
        yield chunk
