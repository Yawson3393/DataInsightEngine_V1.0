# storage/result_store.py

"""
ResultStore: unified output storage for analysis results.

Handles:
- per-task feature results (cell/rack/stack level)
- anomaly detection outputs
- SOH prediction results
- JSON report generation for UI download

Directory layout:
    results_root/
        {task_id}/
            features.json
            anomalies.json
            soh.json
            report.json
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
import threading


_WRITE_LOCK = threading.Lock()


class ResultStore:
    """
    Store analysis results in structured JSON files.
    """

    def __init__(self, root: str = "./results"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    # ------------------------
    # internal helper
    # ------------------------
    def _path(self, task_id: str, name: str) -> Path:
        p = self.root / task_id / name
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def _write_json(self, path: Path, data: Dict[str, Any]):
        with _WRITE_LOCK:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    # ------------------------
    # public APIs
    # ------------------------
    def save_features(self, task_id: str, features: Dict[str, Any]):
        """
        cell-level / rack-level / stack-level computed features
        """
        path = self._path(task_id, "features.json")
        self._write_json(path, features)

    def save_anomalies(self, task_id: str, anomalies: Dict[str, Any]):
        """
        anomaly detector results
        """
        path = self._path(task_id, "anomalies.json")
        self._write_json(path, anomalies)

    def save_soh(self, task_id: str, soh_result: Dict[str, Any]):
        """
        long-term SOH / EOL prediction
        """
        path = self._path(task_id, "soh.json")
        self._write_json(path, soh_result)

    def save_report(self, task_id: str, report: Dict[str, Any]):
        """
        final result delivered to frontend (overview page, downloads)
        """
        path = self._path(task_id, "report.json")
        self._write_json(path, report)

    # ------------------------
    # readers for API (results.py)
    # ------------------------
    def load(self, task_id: str, name: str) -> Optional[Dict[str, Any]]:
        path = self._path(task_id, name)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def load_features(self, task_id: str):
        return self.load(task_id, "features.json")

    def load_anomalies(self, task_id: str):
        return self.load(task_id, "anomalies.json")

    def load_soh(self, task_id: str):
        return self.load(task_id, "soh.json")

    def load_report(self, task_id: str):
        return self.load(task_id, "report.json")

