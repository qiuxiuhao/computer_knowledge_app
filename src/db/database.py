"""SQLite initialization and connection helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "knowledge.db"

CARDS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    scenario TEXT,
    category TEXT,
    tags TEXT,
    summary TEXT,
    content TEXT,
    keywords TEXT,
    source TEXT,
    is_draft INTEGER NOT NULL DEFAULT 0 CHECK (is_draft IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def get_connection(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open a SQLite connection and return rows by column name."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def initialize_database(db_path: str | Path = DEFAULT_DB_PATH) -> Path:
    """Create the SQLite database file and the cards table if needed."""
    path = Path(db_path)
    with get_connection(path) as connection:
        connection.execute(CARDS_TABLE_SQL)
        connection.commit()
    return path

