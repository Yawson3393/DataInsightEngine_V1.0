"""
Parser for cell voltage CSV (e.g. rack1batVol_2024-10-01)

Columns:
  time, V1, V2, V3, ... (224 cells)
Unit: millivolt → volt
"""

from typing import IO, Dict
from .common import iter_csv, fast_float, parse_time


def parse_batvol_csv(fileobj: IO) -> Dict:

    time_list = []
    cell_table = {}   # key: V1, V2, ...

    for row in iter_csv(fileobj):
        ts = parse_time(row.get("time"))
        if ts is None:
            continue

        time_list.append(ts)

        # parse all Vxxx
        for key, val in row.items():
            if key.lower().startswith("v"):
                if key not in cell_table:
                    cell_table[key] = []
                cell_table[key].append(fast_float(val) / 1000.0 if val else None)

    return {
        "time": time_list,
        "voltage": cell_table,   # dict: {"V1": [..], "V2":[..]}
    }
