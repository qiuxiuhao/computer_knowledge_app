"""Tests for backup and Markdown export services."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.services.card_service import create_card
from src.services.data_safety_service import (
    create_manual_backup,
    export_formal_cards_to_markdown,
)


class DataSafetyServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.db_path = self.root / "test_knowledge.db"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_manual_backup_copies_database(self) -> None:
        create_card(
            title="备份测试卡片",
            category="Python",
            db_path=self.db_path,
        )

        backup_path = create_manual_backup(
            db_path=self.db_path,
            backup_dir=self.root / "backups",
        )

        self.assertTrue(backup_path.exists())
        self.assertTrue(backup_path.name.endswith("_manual.db"))
        with sqlite3.connect(backup_path) as connection:
            count = connection.execute("SELECT COUNT(*) FROM cards;").fetchone()[0]

        self.assertEqual(count, 1)

    def test_export_formal_cards_to_markdown_excludes_drafts(self) -> None:
        formal = create_card(
            title="Markdown 导出测试",
            scenario="知识点",
            category="论文笔记",
            tags="Markdown, SQLite",
            summary="导出正式知识卡片。",
            content="## 正文标题\n\n- 第一条内容",
            is_draft=0,
            db_path=self.db_path,
        )
        create_card(
            title="草稿不应该导出",
            is_draft=1,
            db_path=self.db_path,
        )

        exported_paths = export_formal_cards_to_markdown(
            self.root / "exports",
            db_path=self.db_path,
        )

        self.assertEqual(len(exported_paths), 1)
        self.assertIn(f"{int(formal.id):04d}_Markdown_导出测试.md", exported_paths[0].name)

        markdown = exported_paths[0].read_text(encoding="utf-8")
        self.assertIn("# Markdown 导出测试", markdown)
        self.assertIn("| 用途场景 | 知识点 |", markdown)
        self.assertIn("| 分类 | 论文笔记 |", markdown)
        self.assertIn("| 标签 | Markdown, SQLite |", markdown)
        self.assertIn("| 摘要 | 导出正式知识卡片。 |", markdown)
        self.assertIn("| 创建时间 |", markdown)
        self.assertIn("| 更新时间 |", markdown)
        self.assertIn("## 正文标题", markdown)
        self.assertNotIn("草稿不应该导出", markdown)


if __name__ == "__main__":
    unittest.main()
