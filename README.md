# BatteryInsightEngine - Minimal Reference Implementation

## Quickstart
1. Put `.tar.gz` data under `data/`.
2. Create venv and install: `pip install -r backend/requirements.txt`.
3. Start server: `uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000`.
4. Open browser: `http://localhost:8000/`.

## Notes
- This reference is intentionally minimal to be a solid starting point.
- Parsers are streaming/pandas-based. For production-large workloads, replace pandas with Polars for speed.
- Mapping from V/T columns to physical layout is configurable in `config.py` and `modelbuilder.hierarchy`.
- Add persistent metadata DB (SQLite/Postgres) when scaling.
