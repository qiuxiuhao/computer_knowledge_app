"""Tests for the Stage 2 SQLite data layer."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.db.database import initialize_database
from src.services.card_service import (
    create_card,
    delete_card,
    ensure_sample_data_if_empty,
    get_all_draft_cards,
    get_all_formal_cards,
    get_card_by_id,
    insert_sample_data,
    save_draft_as_formal,
    update_card,
)


class DatabaseLayerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_knowledge.db"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_initialize_database_creates_cards_table(self) -> None:
        initialize_database(self.db_path)

        self.assertTrue(self.db_path.exists())
        with sqlite3.connect(self.db_path) as connection:
            columns = [
                row[1]
                for row in connection.execute("PRAGMA table_info(cards);").fetchall()
            ]

        self.assertEqual(
            columns,
            [
                "id",
                "title",
                "scenario",
                "category",
                "tags",
                "summary",
                "content",
                "keywords",
                "source",
                "is_draft",
                "created_at",
                "updated_at",
            ],
        )

    def test_create_read_update_delete_and_convert_draft(self) -> None:
        formal = create_card(
            title="MLP 是什么",
            scenario="知识点",
            category="深度学习",
            tags="MLP, PyTorch",
            summary="MLP 是全连接神经网络结构。",
            content="## MLP\n\n示例内容",
            keywords="MLP, Linear",
            source="课堂笔记",
            is_draft=0,
            db_path=self.db_path,
        )
        draft = create_card(
            title="什么是 CUDA OOM",
            is_draft=1,
            db_path=self.db_path,
        )

        formal_cards = get_all_formal_cards(self.db_path)
        draft_cards = get_all_draft_cards(self.db_path)
        self.assertEqual([card.id for card in formal_cards], [formal.id])
        self.assertEqual([card.id for card in draft_cards], [draft.id])

        loaded = get_card_by_id(formal.id, self.db_path)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.title, "MLP 是什么")

        updated = update_card(
            formal.id,
            db_path=self.db_path,
            summary="更新后的总结",
            tags="MLP, PyTorch, 神经网络",
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.summary, "更新后的总结")
        self.assertEqual(updated.tags, "MLP, PyTorch, 神经网络")

        converted = save_draft_as_formal(draft.id, self.db_path)
        self.assertIsNotNone(converted)
        self.assertEqual(converted.is_draft, 0)
        self.assertEqual(len(get_all_draft_cards(self.db_path)), 0)
        self.assertEqual(len(get_all_formal_cards(self.db_path)), 2)

        self.assertTrue(delete_card(formal.id, self.db_path))
        self.assertIsNone(get_card_by_id(formal.id, self.db_path))
        self.assertFalse(delete_card(formal.id, self.db_path))

    def test_insert_sample_data(self) -> None:
        cards = insert_sample_data(self.db_path)

        self.assertEqual(len(cards), 8)
        self.assertEqual(len(get_all_formal_cards(self.db_path)), 4)
        self.assertEqual(len(get_all_draft_cards(self.db_path)), 4)

    def test_ensure_sample_data_only_inserts_when_empty(self) -> None:
        self.assertTrue(ensure_sample_data_if_empty(self.db_path))
        self.assertFalse(ensure_sample_data_if_empty(self.db_path))
        self.assertEqual(len(get_all_formal_cards(self.db_path)), 4)
        self.assertEqual(len(get_all_draft_cards(self.db_path)), 4)


if __name__ == "__main__":
    unittest.main()
