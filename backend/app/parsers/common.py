"""
Common shared utilities for CSV parsers.
"""

import csv
from datetime import datetime
from typing import IO, Generator


# ---------------------------------------------------------
# 优化 float 转换（比 float() 更快 + 容错）
# ---------------------------------------------------------
def fast_float(x):
    try:
        return float(x)
    except:
        return None


# ---------------------------------------------------------
# 时间解析 yyyy/m/d hh:mm:ss
# ---------------------------------------------------------
def parse_time(s: str):
    try:
        return datetime.strptime(s.strip(), "%Y/%m/%d %H:%M:%S")
    except:
        return None


# ---------------------------------------------------------
# 流式逐行 CSV 读取器
# ---------------------------------------------------------
def iter_csv(fileobj: IO, encoding="utf-8") -> Generator[dict, None, None]:
    """
    Yield one row (dict) at a time.
    fileobj: extracted file object from tar.extractfile()
    """
    wrapper = (line.decode(encoding, errors="ignore") for line in fileobj)
    reader = csv.DictReader(wrapper)
    for row in reader:
        yield row
# 共用工具（time parse, cast）