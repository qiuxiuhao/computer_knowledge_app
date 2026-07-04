"""UI-level Markdown source round-trip tests."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QComboBox, QPlainTextEdit, QTextEdit  # noqa: E402

from src.services.card_service import create_card, create_draft_card, get_all_formal_cards, get_card_by_id  # noqa: E402
from src.ui.block_editor import MarkdownBlockEditor  # noqa: E402
from src.ui.main_window import MainWindow  # noqa: E402
from src.ui.markdown_reader import CodeBlockWidget  # noqa: E402


MARKDOWN_SOURCE = """## AutoDL 环境

中文段落包含 `tmux` 行内代码。

```bash
# 进入项目
cd /root/project
conda activate computer_knowledge_app
python -m src.main --smoke-test
```

结束段落。
"""


class MarkdownRoundTripUiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "knowledge.db"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_edit_save_roundtrip_preserves_markdown_source(self) -> None:
        card = create_card(
            title="Markdown 往返",
            content=MARKDOWN_SOURCE,
            is_draft=0,
            db_path=self.db_path,
        )
        window = MainWindow(self.db_path)
        loaded = get_card_by_id(int(card.id), self.db_path)

        window.show_edit_card_editor(loaded)
        self.assertEqual(window.collect_editor_fields()["content"], MARKDOWN_SOURCE)
        window.save_editor(window.current_editor_card, window.collect_editor_fields())

        saved = get_card_by_id(int(card.id), self.db_path)
        self.assertIn("## AutoDL 环境", saved.content)
        self.assertIn("```bash\n# 进入项目\ncd /root/project\n", saved.content)
        self.assertIn("python -m src.main --smoke-test\n```", saved.content)
        self.assertNotIn("```bash # 进入项目", saved.content)
        window.close()

    def test_existing_markdown_opens_as_blocks_and_saves_content(self) -> None:
        card = create_card(
            title="块解析",
            content=MARKDOWN_SOURCE,
            is_draft=0,
            db_path=self.db_path,
        )
        window = MainWindow(self.db_path)
        loaded = get_card_by_id(int(card.id), self.db_path)

        window.show_edit_card_editor(loaded)
        editor = window.detail_scroll.widget().findChild(MarkdownBlockEditor)
        self.assertIsNotNone(editor)
        self.assertFalse(editor._raw_mode)

        window.save_editor(window.current_editor_card, window.collect_editor_fields())
        saved = get_card_by_id(int(card.id), self.db_path)
        self.assertIn("```bash\n# 进入项目\ncd /root/project\n", saved.content)
        self.assertIn("结束段落。", saved.content)
        window.close()

    def test_new_card_can_save_text_and_code_blocks_as_markdown(self) -> None:
        window = MainWindow(self.db_path)
        window._set_detail_widget(window._build_edit_detail(card=None))

        title_input = window.editor_fields["title"]
        title_input.setText("块编辑新卡片")
        editor = window.editor_fields["content"]
        self.assertIsInstance(editor, MarkdownBlockEditor)

        first_text = editor.findChild(QTextEdit, "BlockTextInput")
        self.assertIsNotNone(first_text)
        first_text.setPlainText("## 安装\n\n先进入项目。")

        editor.add_code_block()
        code_input = editor.findChild(QPlainTextEdit, "BlockCodeInput")
        self.assertIsNotNone(code_input)
        code_input.setPlainText("conda activate computer_knowledge_app\npython -m src.main")
        language_input = editor.findChild(QComboBox, "BlockLanguageSelect")
        self.assertIsNotNone(language_input)
        language_input.setCurrentText("bash")

        window.save_editor(None, window.collect_editor_fields())
        saved_cards = get_all_formal_cards(self.db_path)
        self.assertEqual(saved_cards[0].title, "块编辑新卡片")
        self.assertIn("## 安装", saved_cards[0].content)
        self.assertIn("```bash\nconda activate computer_knowledge_app\npython -m src.main\n```", saved_cards[0].content)
        window.close()

    def test_draft_autosave_uses_block_editor_markdown(self) -> None:
        draft = create_draft_card("块编辑草稿", db_path=self.db_path)
        window = MainWindow(self.db_path)

        window.open_draft_editor(int(draft.id))
        editor = window.editor_fields["content"]
        self.assertIsInstance(editor, MarkdownBlockEditor)
        text_input = editor.findChild(QTextEdit, "BlockTextInput")
        self.assertIsNotNone(text_input)
        text_input.setPlainText("草稿正文")

        self.assertTrue(window.flush_draft_autosave())
        saved = get_card_by_id(int(draft.id), self.db_path)
        self.assertEqual(saved.is_draft, 1)
        self.assertEqual(saved.content, "草稿正文\n")
        window.close()

    def test_parse_failure_uses_raw_markdown_mode_without_block_rewrite(self) -> None:
        original = "说明\n\n```bash\necho hello\n"
        card = create_card(
            title="未闭合代码块",
            content=original,
            is_draft=0,
            db_path=self.db_path,
        )
        window = MainWindow(self.db_path)
        loaded = get_card_by_id(int(card.id), self.db_path)

        window.show_edit_card_editor(loaded)
        editor = window.editor_fields["content"]
        self.assertIsInstance(editor, MarkdownBlockEditor)
        self.assertTrue(editor._raw_mode)
        self.assertEqual(window.collect_editor_fields()["content"], original)

        window.save_editor(window.current_editor_card, window.collect_editor_fields())
        saved = get_card_by_id(int(card.id), self.db_path)
        self.assertEqual(saved.content, original)
        window.close()

    def test_code_copy_does_not_modify_cards_content(self) -> None:
        card = create_card(
            title="复制不改正文",
            content=MARKDOWN_SOURCE,
            is_draft=0,
            db_path=self.db_path,
        )
        window = MainWindow(self.db_path)
        loaded = get_card_by_id(int(card.id), self.db_path)

        preview = window._build_preview_detail(loaded)
        code_block = preview.findChild(CodeBlockWidget)
        self.assertIsNotNone(code_block)
        code_block.copy_code()

        saved = get_card_by_id(int(card.id), self.db_path)
        self.assertEqual(saved.content, MARKDOWN_SOURCE)
        window.close()

    def test_code_block_widget_uses_content_height_without_extra_blank_top(self) -> None:
        card = create_card(
            title="代码块高度",
            content="```bash\nline 1\nline 2\nline 3\n```",
            is_draft=0,
            db_path=self.db_path,
        )
        window = MainWindow(self.db_path)
        loaded = get_card_by_id(int(card.id), self.db_path)

        preview = window._build_preview_detail(loaded)
        code_block = preview.findChild(CodeBlockWidget)
        self.assertIsNotNone(code_block)
        self.assertEqual(code_block.minimumHeight(), code_block.maximumHeight())
        self.assertEqual(code_block.minimumHeight(), 42 + code_block._code_view_height())
        window.close()


if __name__ == "__main__":
    unittest.main()
