"""Tests for the Stage 2 SQLite data layer."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.db.database import initialize_database
from src.services.card_service import (
    create_card,
    create_draft_card,
    delete_card,
    ensure_sample_data_if_empty,
    get_all_draft_cards,
    get_all_formal_cards,
    get_card_by_id,
    get_tag_suggestions,
    insert_sample_data,
    normalize_tags,
    save_draft_as_formal,
    search_cards,
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

    def test_create_draft_card_only_requires_title_and_sorts_newest_first(self) -> None:
        first = create_draft_card("  第一个草稿  ", db_path=self.db_path)
        second = create_draft_card("第二个草稿", db_path=self.db_path)

        self.assertEqual(first.title, "第一个草稿")
        self.assertEqual(first.is_draft, 1)
        self.assertEqual(first.scenario, "")
        self.assertEqual(first.content, "")

        draft_cards = get_all_draft_cards(self.db_path)
        self.assertEqual([card.title for card in draft_cards], ["第二个草稿", "第一个草稿"])

        with self.assertRaises(ValueError):
            create_draft_card("   ", db_path=self.db_path)

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

    def test_search_cards_matches_expected_fields_and_excludes_drafts(self) -> None:
        create_card(
            title="PyTorch 张量维度整理",
            scenario="知识点",
            category="PyTorch",
            tags="tensor, shape",
            summary="记录张量维度变化。",
            content="使用 view 和 reshape 调整维度。",
            keywords="dimension",
            is_draft=0,
            db_path=self.db_path,
        )
        create_card(
            title="AutoDL 训练流程",
            scenario="工作流",
            category="AutoDL",
            tags="server, train",
            summary="远程训练流程。",
            content="启动 tmux 后运行训练脚本。",
            keywords="gpu",
            is_draft=0,
            db_path=self.db_path,
        )
        create_card(
            title="PyTorch 草稿不应出现",
            category="PyTorch",
            tags="tensor",
            content="view reshape",
            is_draft=1,
            db_path=self.db_path,
        )
        create_card(
            title="普通内容匹配",
            category="Python",
            content="这里包含排序关键词。",
            is_draft=0,
            db_path=self.db_path,
        )
        create_card(
            title="排序标题匹配",
            category="Python",
            content="正文没有特殊内容。",
            is_draft=0,
            db_path=self.db_path,
        )

        title_results = search_cards("张量", db_path=self.db_path)
        self.assertEqual([card.title for card in title_results], ["PyTorch 张量维度整理"])

        tag_results = search_cards("server", db_path=self.db_path)
        self.assertEqual([card.title for card in tag_results], ["AutoDL 训练流程"])

        content_results = search_cards("reshape", db_path=self.db_path)
        self.assertEqual([card.title for card in content_results], ["PyTorch 张量维度整理"])

        category_results = search_cards("训练", category="AutoDL", db_path=self.db_path)
        self.assertEqual([card.title for card in category_results], ["AutoDL 训练流程"])

        excluded_by_category = search_cards("训练", category="PyTorch", db_path=self.db_path)
        self.assertEqual(excluded_by_category, [])

        draft_excluded = search_cards("草稿", db_path=self.db_path)
        self.assertEqual(draft_excluded, [])

        ordered_results = search_cards("排序", db_path=self.db_path)
        self.assertEqual(ordered_results[0].title, "排序标题匹配")

    def test_tag_normalization_and_suggestions(self) -> None:
        self.assertEqual(
            normalize_tags(" MLP， PyTorch, MLP,, 神经网络 ， "),
            "MLP, PyTorch, 神经网络",
        )

        card = create_card(
            title="标签清理测试",
            tags=" PyTorch， tensor, PyTorch,, 张量 ",
            is_draft=0,
            db_path=self.db_path,
        )
        self.assertEqual(card.tags, "PyTorch, tensor, 张量")

        updated = update_card(
            int(card.id),
            db_path=self.db_path,
            tags="tensor， shape, tensor,  ",
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.tags, "tensor, shape")
        self.assertEqual(get_tag_suggestions(self.db_path), ["shape", "tensor"])


if __name__ == "__main__":
    unittest.main()
