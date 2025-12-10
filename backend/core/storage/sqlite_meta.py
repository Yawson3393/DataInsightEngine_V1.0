"""
SQLite metadata store
Keeps:
- topology info (stack/rack/module/cell)
- quick lookup for UI
- cached statistics
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import threading

_LOCK = threading.Lock()
DB_PATH = "./storage_meta.sqlite"


def conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    c = conn().cursor()

    # topology
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS topology (
            key TEXT PRIMARY KEY,
            value_json TEXT
        )
        """
    )

    # cached stats
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS stats_cache (
            key TEXT PRIMARY KEY,
            value_json TEXT
        )
        """
    )

    c.connection.commit()
    c.connection.close()


init_db()


class SQLiteMetaStore:
    """
    Store and retrieve metadata as JSON.
    """

    @staticmethod
    def set_topology(key: str, value: Dict[str, Any]):
        with _LOCK:
            c = conn()
            cur = c.cursor()
            cur.execute(
                """
                INSERT OR REPLACE INTO topology (key, value_json)
                VALUES (?, ?)
                """,
                (key, json.dumps(value)),
            )
            c.commit()
            c.close()

    @staticmethod
    def get_topology(key: str) -> Optional[Dict[str, Any]]:
        c = conn()
        cur = c.cursor()
        cur.execute("SELECT value_json FROM topology WHERE key=?", (key,))
        row = cur.fetchone()
        c.close()
        if not row:
            return None
        return json.loads(row[0])

    # ------------------------------------------------------------
    # Stats cache
    # ------------------------------------------------------------

    @staticmethod
    def set_cached_stats(key: str, value: Dict[str, Any]):
        with _LOCK:
            c = conn()
            cur = c.cursor()
            cur.execute(
                """
                INSERT OR REPLACE INTO stats_cache (key, value_json)
                VALUES (?, ?)
                """,
                (key, json.dumps(value)),
            )
            c.commit()
            c.close()

    @staticmethod
    def get_cached_stats(key: str) -> Optional[Dict[str, Any]]:
        c = conn()
        cur = c.cursor()
        cur.execute(
            "SELECT value_json FROM stats_cache WHERE key=?",
            (key,),
        )
        row = cur.fetchone()
        c.close()
        if not row:
            return None
        return json.loads(row[0])
