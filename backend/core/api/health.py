from fastapi import APIRouter
import psutil
import platform
import time

router = APIRouter()

start_time = time.time()


@router.get("/ping")
def ping():
    return {"status": "ok"}


@router.get("/info")
def system_info():
    return {
        "os": platform.system(),
        "cores": psutil.cpu_count(),
        "memory_gb": round(psutil.virtual_memory().total / 1024**3, 2),
    }


@router.get("/metrics")
def metrics():
    uptime = time.time() - start_time
    mem = psutil.virtual_memory()
    return {
        "uptime_sec": round(uptime, 1),
        "memory_used_pct": mem.percent,
        "cpu_used_pct": psutil.cpu_percent(),
    }
# 健康检查、metrics