# backend/app/utils/logger.py
import logging, os
from logging.handlers import RotatingFileHandler

def init_logger():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger("battery")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fh = RotatingFileHandler(f"{log_dir}/engine.log", maxBytes=10*1024*1024, backupCount=5)
        fmt = logging.Formatter('{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}')
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger

logger = init_logger()
