"""
Parser for bank-level summary CSV (bank0summary_2024-10-01)
"""

from typing import IO, Dict
from .common import iter_csv, parse_time, fast_float


def parse_summary_csv(fileobj: IO) -> Dict:
    time_list = []
    volt_list = []
    curr_list = []
    soc_list = []
    soh_list = []

    for row in iter_csv(fileobj):

        ts = parse_time(row.get("time"))
        if ts is None:
            continue

        total_vol = fast_float(row.get("totalVol"))
        total_cur = fast_float(row.get("totalCur"))
        soc = fast_float(row.get("soc"))
        soh = fast_float(row.get("soh"))

        if total_vol is None:
            continue

        time_list.append(ts)
        volt_list.append(total_vol * 0.1)
        curr_list.append(total_cur * 0.1 if total_cur is not None else None)
        soc_list.append(soc * 0.1 if soc is not None else None)
        soh_list.append(soh * 0.1 if soh is not None else None)

    return {
        "time": time_list,
        "totalVol": volt_list,
        "totalCur": curr_list,
        "soc": soc_list,
        "soh": soh_list,
    }
