"""Data safety services for backups and Markdown export."""

from __future__ import annotations

import re
from pathlib import Path

from src.db.database import DEFAULT_DB_PATH, backup_database
from src.models.card import Card
from src.services.card_service import get_all_formal_cards


def create_manual_backup(
    *,
    db_path: str | Path = DEFAULT_DB_PATH,
    backup_dir: str | Path | None = None,
) -> Path:
    """Create a manual SQLite database backup and return the backup path."""
    return backup_database(db_path, backup_dir=backup_dir, reason="manual")


def export_formal_cards_to_markdown(
    export_dir: str | Path,
    *,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> list[Path]:
    """Export all formal cards into Markdown files."""
    target_dir = Path(export_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    exported_paths: list[Path] = []
    for card in get_all_formal_cards(db_path):
        file_path = target_dir / _markdown_filename(card)
        file_path.write_text(_card_to_markdown(card), encoding="utf-8")
        exported_paths.append(file_path)

    return exported_paths


def _markdown_filename(card: Card) -> str:
    title = card.title.strip() or "untitled"
    safe_title = re.sub(r'[\\/:*?"<>|\s]+', "_", title).strip("._")
    safe_title = safe_title[:80] or "untitled"
    prefix = f"{int(card.id):04d}" if card.id is not None else "card"
    return f"{prefix}_{safe_title}.md"


def _card_to_markdown(card: Card) -> str:
    metadata = [
        ("用途场景", card.scenario or "未填写"),
        ("分类", card.category or "未分类"),
        ("标签", card.tags or "暂无"),
        ("摘要", card.summary or "暂无"),
        ("创建时间", card.created_at or "未知"),
        ("更新时间", card.updated_at or "未知"),
    ]

    lines = [
        f"# {card.title}",
        "",
        "| 字段 | 内容 |",
        "|---|---|",
    ]
    for key, value in metadata:
        lines.append(f"| {key} | {_escape_table_cell(value)} |")

    lines.extend(
        [
            "",
            "## 正文",
            "",
            card.content or "",
            "",
        ]
    )
    return "\n".join(lines)


def _escape_table_cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")
