"""Data access functions for knowledge cards."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from src.db.database import DEFAULT_DB_PATH, get_connection, initialize_database
from src.models.card import Card

CARD_FIELDS = (
    "title",
    "scenario",
    "category",
    "tags",
    "summary",
    "content",
    "keywords",
    "source",
    "is_draft",
)

UPDATABLE_FIELDS = set(CARD_FIELDS)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _normalize_is_draft(value: int | bool) -> int:
    return 1 if bool(value) else 0


def create_card(
    *,
    title: str,
    scenario: str = "",
    category: str = "",
    tags: str = "",
    summary: str = "",
    content: str = "",
    keywords: str = "",
    source: str = "",
    is_draft: int | bool = 0,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> Card:
    """Create one formal or draft card and return the saved record."""
    if not title.strip():
        raise ValueError("title cannot be empty")

    initialize_database(db_path)
    timestamp = _now()

    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO cards (
                title, scenario, category, tags, summary, content,
                keywords, source, is_draft, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                title.strip(),
                scenario,
                category,
                tags,
                summary,
                content,
                keywords,
                source,
                _normalize_is_draft(is_draft),
                timestamp,
                timestamp,
            ),
        )
        connection.commit()
        card_id = int(cursor.lastrowid)

    card = get_card_by_id(card_id, db_path=db_path)
    if card is None:
        raise RuntimeError("created card could not be loaded")
    return card


def get_all_formal_cards(db_path: str | Path = DEFAULT_DB_PATH) -> list[Card]:
    """Return all formal cards, newest updated first."""
    return _get_cards_by_draft_state(0, db_path)


def get_all_draft_cards(db_path: str | Path = DEFAULT_DB_PATH) -> list[Card]:
    """Return all draft cards, newest updated first."""
    return _get_cards_by_draft_state(1, db_path)


def get_card_by_id(card_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> Card | None:
    """Return one card by id, or None if it does not exist."""
    initialize_database(db_path)

    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT id, title, scenario, category, tags, summary, content,
                   keywords, source, is_draft, created_at, updated_at
            FROM cards
            WHERE id = ?;
            """,
            (card_id,),
        ).fetchone()

    return Card.from_row(row) if row else None


def update_card(
    card_id: int,
    *,
    db_path: str | Path = DEFAULT_DB_PATH,
    **fields: Any,
) -> Card | None:
    """Update allowed card fields and return the updated card."""
    if not fields:
        raise ValueError("no fields provided for update")

    unknown_fields = set(fields) - UPDATABLE_FIELDS
    if unknown_fields:
        names = ", ".join(sorted(unknown_fields))
        raise ValueError(f"unknown card field(s): {names}")

    if "title" in fields and not str(fields["title"]).strip():
        raise ValueError("title cannot be empty")

    initialize_database(db_path)

    cleaned_fields: dict[str, Any] = {}
    for key, value in fields.items():
        if key == "is_draft":
            cleaned_fields[key] = _normalize_is_draft(value)
        elif key == "title":
            cleaned_fields[key] = str(value).strip()
        else:
            cleaned_fields[key] = value

    cleaned_fields["updated_at"] = _now()
    assignments = ", ".join(f"{field} = ?" for field in cleaned_fields)
    values = list(cleaned_fields.values())
    values.append(card_id)

    with get_connection(db_path) as connection:
        cursor = connection.execute(
            f"UPDATE cards SET {assignments} WHERE id = ?;",
            values,
        )
        connection.commit()
        if cursor.rowcount == 0:
            return None

    return get_card_by_id(card_id, db_path=db_path)


def delete_card(card_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    """Delete one card by id. Return True if a row was deleted."""
    initialize_database(db_path)

    with get_connection(db_path) as connection:
        cursor = connection.execute("DELETE FROM cards WHERE id = ?;", (card_id,))
        connection.commit()
        return cursor.rowcount > 0


def save_draft_as_formal(card_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> Card | None:
    """Convert a draft card into a formal card by setting is_draft to 0."""
    return update_card(card_id, db_path=db_path, is_draft=0)


def insert_sample_data(db_path: str | Path = DEFAULT_DB_PATH) -> list[Card]:
    """Insert a few sample cards for manual database-layer testing."""
    samples = [
        {
            "title": "MLP 是什么，以及 PyTorch 中一般怎么写",
            "scenario": "知识点",
            "category": "深度学习",
            "tags": "MLP, PyTorch, 神经网络, 全连接层",
            "summary": "MLP 是由多个全连接层和激活函数组成的神经网络结构。",
            "content": "## PyTorch 最小代码\n\n```python\nimport torch.nn as nn\n```",
            "keywords": "MLP, Linear, ReLU",
            "source": "",
            "is_draft": 0,
        },
        {
            "title": "什么是 CUDA OOM",
            "scenario": "",
            "category": "",
            "tags": "",
            "summary": "",
            "content": "",
            "keywords": "CUDA OOM, 显存不足",
            "source": "",
            "is_draft": 1,
        },
        {
            "title": "conda 和 pip 的区别",
            "scenario": "",
            "category": "",
            "tags": "",
            "summary": "",
            "content": "",
            "keywords": "conda, pip",
            "source": "",
            "is_draft": 1,
        },
    ]

    return [create_card(db_path=db_path, **sample) for sample in samples]


def _get_cards_by_draft_state(is_draft: int, db_path: str | Path) -> list[Card]:
    initialize_database(db_path)

    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT id, title, scenario, category, tags, summary, content,
                   keywords, source, is_draft, created_at, updated_at
            FROM cards
            WHERE is_draft = ?
            ORDER BY updated_at DESC, id DESC;
            """,
            (is_draft,),
        ).fetchall()

    return [Card.from_row(row) for row in rows]

