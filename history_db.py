"""Persistent SQLite storage for the latest successful rename operation."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Sequence

DATABASE_PATH = Path(__file__).resolve().parent / "rename_history.db"


def initialize_database() -> None:
    """Create the local database and history table when they do not exist."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS rename_history (
                position INTEGER PRIMARY KEY,
                old_path TEXT NOT NULL,
                new_path TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        connection.commit()


def save_last_history(history: Sequence[tuple[Path, Path]]) -> None:
    """Replace stored history with the latest successful rename batch."""
    initialize_database()
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("DELETE FROM rename_history")
        connection.executemany(
            "INSERT INTO rename_history (position, old_path, new_path) VALUES (?, ?, ?)",
            [(index, str(old), str(new)) for index, (old, new) in enumerate(history)],
        )
        connection.commit()


def load_last_history() -> list[tuple[Path, Path]]:
    """Load the latest batch in its original operation order."""
    initialize_database()
    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute(
            "SELECT old_path, new_path FROM rename_history ORDER BY position"
        ).fetchall()
    return [(Path(old), Path(new)) for old, new in rows]


def clear_last_history() -> None:
    """Delete persistent undo history after a successful undo."""
    initialize_database()
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("DELETE FROM rename_history")
        connection.commit()


def history_is_undoable(history: Sequence[tuple[Path, Path]]) -> bool:
    """Return true only when all renamed files still exist at their new paths."""
    return bool(history) and all(new.is_file() for _old, new in history)


def load_preferences() -> tuple[str, bool]:
    """Load the last language and theme, using English/light on first launch."""
    initialize_database()
    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = dict(connection.execute("SELECT key, value FROM app_settings").fetchall())
    language = rows.get("language", "en")
    if language not in {"en", "ar"}:
        language = "en"
    dark_mode = rows.get("dark_mode", "0") == "1"
    return language, dark_mode


def save_preferences(language: str, dark_mode: bool) -> None:
    """Persist the current language and theme in the local database."""
    if language not in {"en", "ar"}:
        raise ValueError("Unsupported language")
    initialize_database()
    values = [("language", language), ("dark_mode", "1" if dark_mode else "0")]
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.executemany(
            "INSERT INTO app_settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            values,
        )
        connection.commit()
