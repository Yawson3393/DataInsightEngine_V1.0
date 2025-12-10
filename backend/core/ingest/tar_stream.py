"""
Streaming utilities for reading .tar.gz files WITHOUT extraction.

stream_tar_members(tar_path):
    Yields (member_name, fileobj) for all files inside tar.gz.

This is optimized for:
- low memory footprint
- sequential processing
"""

import tarfile
from pathlib import Path
from typing import Generator, Tuple, IO


def stream_tar_members(tar_path: str) -> Generator[Tuple[str, IO], None, None]:
    """
    Stream members inside tar.gz file.
    Parameters
    ----------
    tar_path: str
        path to tar.gz

    Yields
    ------
    (member_name : str, fileobj : IO)
    """

    tar_path = Path(tar_path)

    if not tar_path.exists():
        raise FileNotFoundError(f"tar.gz not found: {tar_path}")

    # r:gz = gzip streaming reader
    with tarfile.open(tar_path, "r:gz") as tf:
        for member in tf.getmembers():
            if member.isfile():
                fileobj = tf.extractfile(member)
                if fileobj is None:
                    continue
                yield member.name, fileobj
