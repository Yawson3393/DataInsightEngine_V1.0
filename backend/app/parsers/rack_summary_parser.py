"""
Parser for rack-level summary CSV (rack1summary_2024-10-01)
"""

from typing import IO, Dict
from .common import iter_csv, fast_float, parse_time


def parse_rack_summary_csv(fileobj: IO) -> Dict:

    out = {
        "time": [],
        "totalVol": [],
        "totalCurrent": [],
        "soc": [],
        "soh": [],
        "maxSingleVoltage": [],
        "minSingleVoltage": [],
        "maxSingleTemp": [],
        "minSingleTemp": [],
    }

    for row in iter_csv(fileobj):

        ts = parse_time(row.get("time"))
        if ts is None:
            continue

        out["time"].append(ts)
        out["totalVol"].append(fast_float(row.get("totalVol")) * 0.1)
        out["totalCurrent"].append(fast_float(row.get("totalCurrent")) * 0.1)
        out["soc"].append(fast_float(row.get("soc")) * 0.1)
        out["soh"].append(fast_float(row.get("soh")) * 0.1)

        # 单体电压/温度
        out["maxSingleVoltage"].append(fast_float(row.get("maxSingleVoltageValue")) * 0.001)
        out["minSingleVoltage"].append(fast_float(row.get("minSingleVoltageValue")) * 0.001)

        out["maxSingleTemp"].append(fast_float(row.get("maxSingleTempValue")) * 0.1)
        out["minSingleTemp"].append(fast_float(row.get("minSingleTempValue")) * 0.1)

    return out
