# backend/app/tasks/pipeline.py
import os, uuid, multiprocessing, time
from .worker import process_tar_single
from .progress import ProgressManager
from ..config import settings
from ..utils.logger import logger

def start_analysis_task(files: list[str]) -> str:
    task_id = str(uuid.uuid4())
    p = multiprocessing.Process(target=_run, args=(task_id, files))
    p.daemon = True
    p.start()
    return task_id

def _run(task_id, files):
    pm = ProgressManager()
    pm.update(task_id, "started", 1)
    out_root = settings.OUTPUT_ROOT
    os.makedirs(out_root, exist_ok=True)
    # create task output folder
    task_out = os.path.join(out_root, task_id)
    os.makedirs(task_out, exist_ok=True)
    # process each file sequentially (could be parallelized)
    total = len(files)
    for idx, fname in enumerate(files):
        pm.update(task_id, f"processing {fname}", int( idx/total*80 ))
        tar_path = os.path.join(settings.DATA_ROOT, fname)
        try:
            res = process_tar_single(task_id, tar_path, pm=pm)
            # optionally save res summary to a file in task_out
            import json
            with open(os.path.join(task_out, f"{os.path.basename(fname)}.json"), "w", encoding="utf-8") as f:
                json.dump(res, f, default=str)
        except Exception as e:
            logger.exception("error processing %s", fname)
            pm.update(task_id, f"error processing {fname}", 0, info=str(e))
    pm.update(task_id, "saving", 95)
    time.sleep(0.5)
    pm.update(task_id, "done", 100)
