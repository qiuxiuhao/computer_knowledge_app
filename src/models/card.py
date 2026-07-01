"""Knowledge card data model."""

from __future__ import annotations

from dataclasses import dataclass
from sqlite3 import Row


@dataclass(frozen=True)
class Card:
    """A formal or draft knowledge card stored in the cards table."""

    id: int | None
    title: str
    scenario: str = ""
    category: str = ""
    tags: str = ""
    summary: str = ""
    content: str = ""
    keywords: str = ""
    source: str = ""
    is_draft: int = 0
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_row(cls, row: Row) -> "Card":
        return cls(
            id=row["id"],
            title=row["title"],
            scenario=row["scenario"] or "",
            category=row["category"] or "",
            tags=row["tags"] or "",
            summary=row["summary"] or "",
            content=row["content"] or "",
            keywords=row["keywords"] or "",
            source=row["source"] or "",
            is_draft=int(row["is_draft"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

