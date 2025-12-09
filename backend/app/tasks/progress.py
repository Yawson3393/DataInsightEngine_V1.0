# backend/app/tasks/progress.py
import threading

class ProgressManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._progress = {}
        return cls._instance

    def update(self, task_id, stage, percent, info=None):
        self._progress[task_id] = {"stage": stage, "percent": percent, "info": info}

    def get_progress(self, task_id):
        return self._progress.get(task_id, {"stage":"pending","percent":0})

    def get_progress_snapshot(self):
        return self._progress

    def cancel(self, task_id):
        self._progress[task_id] = {"stage":"cancelled","percent":0}
