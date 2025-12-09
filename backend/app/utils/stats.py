"""
Online statistics utilities used by analysis layer.
Supports:
- Welford mean/variance
- Online min/max
- Rolling windows
- Percentile aggregator (approx)
"""

import math
from collections import deque
from typing import Optional, Iterable


class Welford:
    """
    Online mean/variance/std aggregator.
    """

    def __init__(self):
        self.count = 0
        self.mean = 0.0
        self.M2 = 0.0
        self.min = float("inf")
        self.max = float("-inf")

    def update(self, x: float):
        self.count += 1

        # update min/max
        if x < self.min:
            self.min = x
        if x > self.max:
            self.max = x

        # Welford algorithm
        delta = x - self.mean
        self.mean += delta / self.count
        delta2 = x - self.mean
        self.M2 += delta * delta2

    @property
    def variance(self) -> float:
        return self.M2 / (self.count - 1) if self.count > 1 else 0.0

    @property
    def std(self) -> float:
        return math.sqrt(self.variance)

    def to_dict(self):
        return {
            "count": self.count,
            "mean": self.mean,
            "min": self.min,
            "max": self.max,
            "std": self.std,
            "variance": self.variance,
        }


class RollingWindow:
    """
    Generic rolling window for streaming data.
    """

    def __init__(self, size: int):
        self.size = size
        self.q = deque()

    def update(self, x):
        self.q.append(x)
        if len(self.q) > self.size:
            self.q.popleft()

    def values(self) -> Iterable:
        return list(self.q)

    def mean(self) -> float:
        if not self.q:
            return 0.0
        return sum(self.q) / len(self.q)


class HistogramApprox:
    """
    Approximate percentile using fixed-bin histogram.
    Suitable for 100k–10M values.
    """

    def __init__(self, lo: float, hi: float, bins: int = 2000):
        self.lo = lo
        self.hi = hi
        self.bins = bins
        self.counts = [0] * bins
        self.total = 0
        self.bin_width = (hi - lo) / bins

    def update(self, x: float):
        if x < self.lo:
            idx = 0
        elif x >= self.hi:
            idx = self.bins - 1
        else:
            idx = int((x - self.lo) / self.bin_width)
        self.counts[idx] += 1
        self.total += 1

    def percentile(self, p: float) -> float:
        """
        p ∈ [0, 100]
        """
        target = p / 100 * self.total
        acc = 0
        for i, c in enumerate(self.counts):
            acc += c
            if acc >= target:
                return self.lo + i * self.bin_width
        return self.hi


def derivative(prev: float, cur: float, dt: float) -> float:
    """
    compute dV/dt or dT/dt
    """
    if dt <= 0:
        return 0.0
    return (cur - prev) / dt
