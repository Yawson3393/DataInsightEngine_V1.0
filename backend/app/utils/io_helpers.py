"""
IO helpers for streaming and chunk processing.
Supports:
- Chunked CSV line streaming
- Welford aggregators
- Online min/max
- Safe float cast
"""

from typing import Iterable, Callable, List, Optional
import io


def iter_chunks(
    fileobj: io.BufferedReader,
    chunk_size: int = 65536,
) -> Iterable[bytes]:
    """
    Stream fileobj by chunk_size.
    """
    while True:
        data = fileobj.read(chunk_size)
        if not data:
            break
        yield data


def read_csv_lines_stream(fileobj, encoding="utf-8"):
    """
    Read CSV lines streaming; fileobj is tar.extractfile output.
    """
    buf = io.BufferedReader(fileobj)
    for line in buf:
        yield line.decode(encoding, errors="ignore").rstrip("\n")


def safe_float(x) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")


class OnlineMinMax:
    def __init__(self):
        self.min = float("inf")
        self.max = float("-inf")

    def update(self, x: float):
        if x < self.min:
            self.min = x
        if x > self.max:
            self.max = x

    def to_dict(self):
        return {"min": self.min, "max": self.max}


class AggGroup:
    """
    Group of Welford aggregators for entire module/rack.
    """

    def __init__(self, size: int):
        from .stats import Welford
        self.size = size
        self.items = [Welford() for _ in range(size)]

    def update(self, values: List[float]):
        for i, x in enumerate(values):
            self.items[i].update(x)

    def to_dict(self):
        return [w.to_dict() for w in self.items]
