"""
Map T1..Tn temperature sensors to (rack, module, pos)
"""

from typing import Dict, Tuple
from .hierarchy import Stack


class TemperatureMapper:
    """
    Build global_temp_id → (rack, module, pos)
    """

    def __init__(self, stack: Stack):
        self.lookup: Dict[int, Tuple[int, int, int]] = {}
        for rack in stack.racks:
            for module in rack.modules:
                for temp in module.temps:
                    self.lookup[temp.temp_id] = (
                        rack.rack_id,
                        module.module_id,
                        temp.pos,
                    )

    def map(self, temp_id: int):
        return self.lookup.get(temp_id, None)

    def map_many(self, ids):
        return [self.map(i) for i in ids]


# ------------------------------------------------------------------
# DF-based helper
# ------------------------------------------------------------------

def attach_temp_position(df, mapper: TemperatureMapper):
    """
    df columns: T1, T2, ...
    Output long-form:
        temp_id, rack, module, pos, temperature
    """
    import polars as pl

    out = []

    for col in df.columns:
        if not col.startswith("T"):
            continue
        idx = int(col[1:])
        pos = mapper.map(idx)
        if pos is None:
            continue

        rack, module, pos_idx = pos

        tmp = df.select(
            pl.lit(idx).alias("temp_id"),
            pl.lit(rack).alias("rack"),
            pl.lit(module).alias("module"),
            pl.lit(pos_idx).alias("pos"),
            pl.col(col).alias("temperature"),
            pl.col("timestamp"),
        )
        out.append(tmp)

    if not out:
        return df

    return pl.concat(out)
