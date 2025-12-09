"""
Map V1..Vn to (rack, module, row, col)
"""

from typing import Dict, Tuple
from .hierarchy import Stack


class VoltageMapper:
    """
    Build global_voltage_id → (rack_id, module_id, row, col)
    """

    def __init__(self, stack: Stack):
        self.lookup: Dict[int, Tuple[int, int, int, int]] = {}
        for rack in stack.racks:
            for module in rack.modules:
                for cell in module.cells:
                    self.lookup[cell.cell_id] = (
                        rack.rack_id,
                        module.module_id,
                        cell.row,
                        cell.col,
                    )

    def map(self, cell_id: int):
        """
        Return (rack, module, row, col)
        """
        return self.lookup.get(cell_id, None)

    def map_many(self, ids):
        return [self.map(i) for i in ids]


# ------------------------------------------------------------------
# DF-based helper
# ------------------------------------------------------------------

def attach_voltage_position(df, mapper: VoltageMapper):
    """
    df columns: V1, V2, V3 ...
    Convert them into long-form with position info.
    Produces columns:
        cell_id, rack, module, row, col, voltage
    """
    import polars as pl

    out = []

    for col in df.columns:
        if not col.startswith("V"):
            continue
        idx = int(col[1:])
        pos = mapper.map(idx)
        if pos is None:
            continue

        rack, module, row, col_index = pos

        tmp = df.select(
            pl.lit(idx).alias("cell_id"),
            pl.lit(rack).alias("rack"),
            pl.lit(module).alias("module"),
            pl.lit(row).alias("row"),
            pl.lit(col_index).alias("col"),
            pl.col(col).alias("voltage"),
            pl.col("timestamp"),
        )
        out.append(tmp)

    if not out:
        return df

    return pl.concat(out)
