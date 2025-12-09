"""
Timeline & hierarchical alignment:

1) Build unified time grid (5s interval)
2) Align all bank/rack/module/cell values to the same time grid
3) Construct module/cell topology (32 cells per module, 20 temp sensors)
"""

import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta

from .interpolation import sync_and_interp
from ..logging_cfg import get_task_logger


# ---------------------------------------------------------
# Build time grid
# ---------------------------------------------------------
def build_time_grid(time_lists: List[List[datetime]], step_sec=5) -> List[datetime]:
    """
    union of all timestamps → min/max → generate dense grid
    """
    all_ts = []
    for ts in time_lists:
        all_ts.extend(ts)

    if not all_ts:
        return []

    tmin = min(all_ts)
    tmax = max(all_ts)

    grid = []
    cur = tmin
    while cur <= tmax:
        grid.append(cur)
        cur += timedelta(seconds=step_sec)

    return grid


# ---------------------------------------------------------
# Align summary data (bank & rack)
# ---------------------------------------------------------
def align_summary(summary_raw: Dict, time_grid: List[datetime]) -> Dict:
    """
    summary_raw example:
      {
        "time": [...],
        "totalVol": [...],
        ...
      }
    """
    return {
        "time": time_grid,
        "totalVol": sync_and_interp(summary_raw["time"], {"v": summary_raw["totalVol"]}, time_grid)["v"],
        "totalCur": sync_and_interp(summary_raw["time"], {"c": summary_raw.get("totalCur", [])}, time_grid)["c"],
        "soc": sync_and_interp(summary_raw["time"], {"soc": summary_raw.get("soc", [])}, time_grid)["soc"],
        "soh": sync_and_interp(summary_raw["time"], {"soh": summary_raw.get("soh", [])}, time_grid)["soh"],
    }


# ---------------------------------------------------------
# Align batVol (cell voltages)
# ---------------------------------------------------------
def align_batvol(vol_raw: Dict, time_grid: List[datetime]) -> Dict[str, List]:
    """
    vol_raw:
      {
        "time": [...],
        "voltage": {"V1":[...], "V2":[...], ...}
      }
    """
    return sync_and_interp(vol_raw["time"], vol_raw["voltage"], time_grid, mode="linear")


# ---------------------------------------------------------
# Align batTemp (temperature sensors)
# ---------------------------------------------------------
def align_battemp(temp_raw: Dict, time_grid: List[datetime]) -> Dict[str, List]:
    """
    temp_raw:
      {
        "time": [...],
        "temp": {"T1":[...], "T2":[...], ...}
      }
    """
    return sync_and_interp(temp_raw["time"], temp_raw["temp"], time_grid, mode="ffill")


# ---------------------------------------------------------
# Build hierarchical modules
# ---------------------------------------------------------
def build_module_structure(vol_aligned: Dict[str, List], temp_aligned: Dict[str, List], config) -> Dict:
    """
    config:
      CELLS_PER_MODULE = 32
      TEMP_PER_MODULE  = 20

    vol_aligned: {"V1":[...], "V2":[...], ...}
    """

    cells_per_mod = config.CELLS_PER_MODULE
    temp_per_mod = config.TEMP_PER_MODULE

    # total cells: e.g. 224 = 7 modules * 32 cells
    all_cell_keys = sorted(vol_aligned.keys(), key=lambda x: int(x[1:]))

    modules = {}
    num_modules = len(all_cell_keys) // cells_per_mod

    for m in range(num_modules):
        mod_id = f"module{m+1}"

        # slice cell indices
        cell_keys = all_cell_keys[m*cells_per_mod:(m+1)*cells_per_mod]

        # gather voltage T × N
        volt_mat = np.stack([vol_aligned[k] for k in cell_keys], axis=1)  # shape: (T, 32)

        # temperatures
        # T1~T20 per module (temperature sensors)
        start_temp = m * temp_per_mod + 1
        temp_keys = [f"T{i}" for i in range(start_temp, start_temp + temp_per_mod)]
        temp_mat = np.stack([temp_aligned[k] for k in temp_keys], axis=1)  # shape: (T,20)

        modules[mod_id] = {
            "voltage": volt_mat.tolist(),
            "temp": temp_mat.tolist(),
        }

    return modules


# ---------------------------------------------------------
# MAIN ENTRY
# ---------------------------------------------------------
def align_day_data(day_raw: Dict[str, Any], config) -> Dict[str, Any]:
    """
    day_raw structure:
      {
        "summary": {"bank": {...}},
        "rack": {
            "rack1": {
                "summary": {...},
                "batvol": {...},
                "battemp": {...}
            },
            ...
      }
    """

    log = get_task_logger("align")

    # Collect all timelines
    tlists = []

    # bank
    if "bank" in day_raw["summary"]:
        tlists.append(day_raw["summary"]["bank"]["time"])

    # rack
    for rack_id, rack in day_raw["rack"].items():
        if "summary" in rack:
            tlists.append(rack["summary"]["summary"]["time"] if "summary" in rack["summary"] else rack["summary"]["time"])
        if "batvol" in rack:
            tlists.append(rack["batvol"]["time"])
        if "battemp" in rack:
            tlists.append(rack["battemp"]["time"])

    # Build unified time grid
    time_grid = build_time_grid(tlists, step_sec=config.TIME_STEP_SEC)

    aligned = {
        "time": time_grid,
        "bank": {},
        "rack": {},
    }

    # ---------------------------------------------------------
    # BANK summary
    # ---------------------------------------------------------
    if "bank" in day_raw["summary"]:
        log.info("Aligning bank summary...")
        aligned["bank"] = align_summary(day_raw["summary"]["bank"], time_grid)

    # ---------------------------------------------------------
    # RACKS
    # ---------------------------------------------------------
    for rack_id, rack in day_raw["rack"].items():
        log.info(f"Aligning {rack_id}")

        rack_out = {}

        # rack summary
        if "summary" in rack:
            rack_out["summary"] = align_summary(rack["summary"], time_grid)

        # voltage
        if "batvol" in rack:
            vol_aligned = align_batvol(rack["batvol"], time_grid)
        else:
            vol_aligned = {}

        # temperature
        if "battemp" in rack:
            temp_aligned = align_battemp(rack["battemp"], time_grid)
        else:
            temp_aligned = {}

        # module structure
        if vol_aligned and temp_aligned:
            modules = build_module_structure(vol_aligned, temp_aligned, config)
            rack_out["modules"] = modules

        aligned["rack"][rack_id] = rack_out

    return aligned
