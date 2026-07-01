"""SQLite initialization and connection helpers."""

from __future__ import annotations

import os
import shutil
import sqlite3
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

APP_ID = "computer_knowledge_app"
APP_SUPPORT_PARENT = Path.home() / "Library" / "Application Support"
SCHEMA_VERSION = 1
DATABASE_PATH_ENV = "COMPUTER_KNOWLEDGE_APP_DB_PATH"

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

APP_META_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS app_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

Migration = Callable[[sqlite3.Connection], None]
MIGRATIONS: dict[int, Migration] = {}


def get_user_data_dir() -> Path:
    """Return the macOS Application Support directory for real user data."""
    return APP_SUPPORT_PARENT / APP_ID


def get_backup_dir() -> Path:
    """Return the default backup directory for real user data."""
    return get_user_data_dir() / "backups"


def ensure_app_directories() -> None:
    """Create the application data and backup directories if needed."""
    get_user_data_dir().mkdir(parents=True, exist_ok=True)
    get_backup_dir().mkdir(parents=True, exist_ok=True)


def get_database_path() -> Path:
    """Return the unified database path for development and packaged runtime."""
    override = os.environ.get(DATABASE_PATH_ENV)
    if override:
        return Path(override).expanduser()

    return get_user_data_dir() / "knowledge.db"


DEFAULT_DB_PATH = get_database_path()


def get_connection(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open a SQLite connection and return rows by column name."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def get_schema_version(db_path: str | Path = DEFAULT_DB_PATH) -> int:
    """Return the current schema version recorded in app_meta."""
    path = Path(db_path)
    if not path.exists():
        return 0

    with get_connection(path) as connection:
        table_exists = connection.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table' AND name = 'app_meta';
            """
        ).fetchone()
        if table_exists is None:
            return 0

        row = connection.execute(
            "SELECT value FROM app_meta WHERE key = 'schema_version';"
        ).fetchone()

    return int(row["value"]) if row else 0


def set_schema_version(
    connection: sqlite3.Connection,
    version: int = SCHEMA_VERSION,
) -> None:
    """Persist the schema version in app_meta."""
    connection.execute(
        """
        INSERT INTO app_meta (key, value)
        VALUES ('schema_version', ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value;
        """,
        (str(version),),
    )


def backup_database(
    db_path: str | Path = DEFAULT_DB_PATH,
    *,
    backup_dir: str | Path | None = None,
    reason: str = "manual",
) -> Path:
    """Copy the SQLite database into the backup directory and return the file path."""
    path = Path(db_path)
    if not path.exists():
        initialize_database(path)

    target_dir = Path(backup_dir) if backup_dir is not None else get_backup_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    safe_reason = "".join(
        character if character.isalnum() or character in ("-", "_") else "_"
        for character in reason.strip()
    ) or "manual"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_path = target_dir / f"knowledge_{timestamp}_{safe_reason}.db"
    shutil.copy2(path, backup_path)
    return backup_path


def migrate_database(
    db_path: str | Path,
    *,
    current_version: int,
    target_version: int = SCHEMA_VERSION,
) -> None:
    """Run schema migrations in order, backing up the database first."""
    if current_version >= target_version:
        return

    backup_database(
        db_path,
        reason=f"pre_migration_v{current_version}_to_v{target_version}",
    )

    version = current_version
    while version < target_version:
        next_version = version + 1
        migration = MIGRATIONS.get(next_version)
        if migration is None:
            raise RuntimeError(f"missing migration for schema version {next_version}")

        with get_connection(db_path) as connection:
            migration(connection)
            set_schema_version(connection, next_version)
            connection.commit()

        version = next_version


def initialize_database(db_path: str | Path = DEFAULT_DB_PATH) -> Path:
    """Create tables, initialize schema version, and run needed migrations."""
    path = Path(db_path)
    if path == get_database_path():
        ensure_app_directories()

    database_existed = path.exists()
    with get_connection(path) as connection:
        connection.execute(CARDS_TABLE_SQL)
        connection.execute(APP_META_TABLE_SQL)
        row = connection.execute(
            "SELECT value FROM app_meta WHERE key = 'schema_version';"
        ).fetchone()
        version = int(row["value"]) if row else 0
        if version == 0:
            version = 1 if database_existed else SCHEMA_VERSION
            set_schema_version(connection, version)
        connection.commit()

    if version > SCHEMA_VERSION:
        raise RuntimeError(
            f"database schema version {version} is newer than supported {SCHEMA_VERSION}"
        )

    if version < SCHEMA_VERSION:
        migrate_database(path, current_version=version, target_version=SCHEMA_VERSION)

    return path
