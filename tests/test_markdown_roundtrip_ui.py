"""UI-level Markdown source round-trip tests."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from src.services.card_service import create_card, get_card_by_id  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()

