import sqlite3
from pathlib import Path


def get_db_path(base_path: Path) -> Path:
    return base_path / "kamba_farma.db"


def connect(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
