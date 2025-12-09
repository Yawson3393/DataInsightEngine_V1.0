# backend/app/storage/parquet_store.py
import os, json, zipfile
from ..config import settings

class ParquetStore:
    def __init__(self, task_id):
        self.task_id = task_id
        self.root = os.path.join(settings.OUTPUT_ROOT, task_id)
        os.makedirs(self.root, exist_ok=True)

    def save_summary_csv(self, name, df):
        path = os.path.join(self.root, f"{name}.csv")
        df.to_csv(path, index=False)
        return path

    def get_zip_path(self):
        zip_path = os.path.join(self.root, f"{self.task_id}_outputs.zip")
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.root):
                for fn in files:
                    zf.write(os.path.join(root, fn), arcname=fn)
        return {"zip": zip_path}

    def load_overview(self):
        # simple: return a list of CSVs
        files = [f for f in os.listdir(self.root) if f.endswith('.csv')]
        return {"files": files}
