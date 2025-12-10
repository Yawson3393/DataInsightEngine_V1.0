"""
Parser for cell temperature CSV (e.g. rack1batTemp_2024-10-01)

Columns:
  time, T1, T2, T3, ... (140 temperature sensors)
Unit: 0.1°C → °C
"""

from typing import IO, Dict
from .common import iter_csv, fast_float, parse_time


def parse_battemp_csv(fileobj: IO) -> Dict:

    time_list = []
    temp_table = {}   # {"T1": [...], "T2": [...]}

    for row in iter_csv(fileobj):
        ts = parse_time(row.get("time"))
        if ts is None:
            continue

        time_list.append(ts)

        for key, val in row.items():
            if key.lower().startswith("t"):
                if key not in temp_table:
                    temp_table[key] = []
                temp_table[key].append(fast_float(val) * 0.1 if val else None)

    return {
        "time": time_list,
        "temp": temp_table,
    }
