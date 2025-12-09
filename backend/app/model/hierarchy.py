"""
Physical hierarchy (Stack → Rack → Module → Cell)
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class Cell:
    cell_id: int            # global index inside a rack
    module_id: int          # module index inside rack
    row: int                # row inside module
    col: int                # col inside module


@dataclass
class TemperatureSensor:
    temp_id: int            # global index inside a rack
    module_id: int
    pos: int                # relative position


@dataclass
class Module:
    module_id: int
    n_rows: int
    n_cols: int
    n_cells: int
    n_temp: int
    cells: List[Cell]
    temps: List[TemperatureSensor]


@dataclass
class Rack:
    rack_id: int
    modules: List[Module]

    @property
    def n_cells_total(self) -> int:
        return sum(m.n_cells for m in self.modules)

    @property
    def n_temps_total(self) -> int:
        return sum(m.n_temp for m in self.modules)


@dataclass
class Stack:
    stack_id: int
    racks: List[Rack]


# -------------------------------------------------------------------
# Builder
# -------------------------------------------------------------------

class HierarchyBuilder:
    """
    Build topology from config values.
    """

    def __init__(
        self,
        n_racks: int = 2,
        n_modules: int = 7,
        cell_rows: int = 4,
        cell_cols: int = 8,
        temp_per_module: int = 20,
    ):
        self.n_racks = n_racks
        self.n_modules = n_modules
        self.cell_rows = cell_rows
        self.cell_cols = cell_cols
        self.n_cells_per_module = cell_rows * cell_cols
        self.temp_per_module = temp_per_module

    def build(self, stack_id: int) -> Stack:
        racks = []

        for r in range(self.n_racks):
            modules = []
            global_cell_idx = 1
            global_temp_idx = 1

            for m in range(self.n_modules):
                # build cells
                cells = []
                for row in range(self.cell_rows):
                    for col in range(self.cell_cols):
                        c = Cell(
                            cell_id=global_cell_idx,
                            module_id=m + 1,
                            row=row,
                            col=col,
                        )
                        cells.append(c)
                        global_cell_idx += 1

                # build temperature sensors
                temps = []
                for t in range(self.temp_per_module):
                    temp = TemperatureSensor(
                        temp_id=global_temp_idx,
                        module_id=m + 1,
                        pos=t,
                    )
                    temps.append(temp)
                    global_temp_idx += 1

                modules.append(
                    Module(
                        module_id=m + 1,
                        n_rows=self.cell_rows,
                        n_cols=self.cell_cols,
                        n_cells=len(cells),
                        n_temp=len(temps),
                        cells=cells,
                        temps=temps,
                    )
                )

            racks.append(Rack(rack_id=r + 1, modules=modules))

        return Stack(stack_id=stack_id, racks=racks)
