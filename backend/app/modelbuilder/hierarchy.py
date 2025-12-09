# backend/app/modelbuilder/hierarchy.py
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Cell:
    id: str
    row: int = 0
    col: int = 0

@dataclass
class Module:
    id: str
    cells: List[Cell] = field(default_factory=list)

@dataclass
class Rack:
    id: str
    modules: List[Module] = field(default_factory=list)

@dataclass
class Heap:
    id: str
    racks: List[Rack] = field(default_factory=list)

def build_default_hierarchy(racks=2, modules_per_rack=7, cells_per_module=32, rows=4, cols=8):
    heap = Heap(id="heap0")
    cid = 1
    for r in range(racks):
        rack = Rack(id=f"rack{r+1}")
        for m in range(modules_per_rack):
            mod = Module(id=f"m{m+1}")
            for i in range(cells_per_module):
                row = i // cols
                col = i % cols
                mod.cells.append(Cell(id=f"V{cid}", row=row, col=col))
                cid += 1
            rack.modules.append(mod)
        heap.racks.append(rack)
    return heap
