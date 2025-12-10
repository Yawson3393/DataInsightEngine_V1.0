"""
Interpolation utilities for time alignment.
Supports:
    - linear interpolation
    - forward fill
    - combined sync + interpolate
"""

import numpy as np
from typing import List, Tuple, Dict


# ---------------------------------------------------------
# 1D linear interpolation (NaN-safe)
# ---------------------------------------------------------
def linear_interp_series(x: List[float], y: List[float], xi: List[float]) -> np.ndarray:
    """
    x : original timestamps (float seconds)
    y : original values
    xi: target timestamps
    """
    x = np.array(x)
    y = np.array(y)
    xi = np.array(xi)

    # remove NaNs and invalid
    valid = ~np.isnan(y)
    if valid.sum() < 2:
        # return NaNs
        return np.full_like(xi, np.nan, dtype=float)

    return np.interp(xi, x[valid], y[valid], left=np.nan, right=np.nan)


# ---------------------------------------------------------
# Forward fill (useful for temperature)
# ---------------------------------------------------------
def forward_fill(series: List[float]) -> List[float]:
    out = []
    last = None
    for v in series:
        if v is not None and not np.isnan(v):
            last = v
        out.append(last)
    return out


# ---------------------------------------------------------
# Sync time & interpolate
# ---------------------------------------------------------
def sync_and_interp(
    time_src: List,
    values: Dict[str, List[float]],
    time_grid: List,
    mode="linear",
) -> Dict[str, List]:

    # convert timestamps to seconds
    t0_src = np.array([t.timestamp() for t in time_src], dtype=float)
    t0_grid = np.array([t.timestamp() for t in time_grid], dtype=float)

    out = {}

    for key, arr in values.items():
        arr = np.array(arr, dtype=float)

        if mode == "linear":
            res = linear_interp_series(t0_src, arr, t0_grid)
        else:  # ffill
            arr_ff = forward_fill(arr.tolist())
            # re-map onto grid (nearest)
            res = linear_interp_series(
                t0_src, np.array(arr_ff, float), t0_grid
            )

        out[key] = res.tolist()

    return out
