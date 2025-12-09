# backend/app/ingest/tar_stream.py
import tarfile, io
from typing import Iterator, Tuple
from ..utils.logger import logger

def iter_members(tar_path: str):
    """Yield (member_name, fileobj) for regular files inside tar.gz"""
    with tarfile.open(tar_path, "r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            f = tar.extractfile(member)
            if f is None:
                continue
            yield member.name, f

def find_members_by_pattern(tar_path: str, patterns: list[str]):
    """Return dict pattern->list of member names found"""
    found = {p: [] for p in patterns}
    with tarfile.open(tar_path, "r:gz") as tar:
        for m in tar.getmembers():
            name = m.name.lower()
            for p in patterns:
                if p.lower() in name and name.endswith('.csv'):
                    found[p].append(m.name)
    return found
