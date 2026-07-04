"""Block-based Markdown editor widgets."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.utils.markdown_blocks import (
    DEFAULT_CODE_LANGUAGES,
    MarkdownBlock,
    MarkdownBlockParseError,
    collect_code_languages,
    parse_markdown_blocks,
    serialize_markdown_blocks,
)


class MarkdownBlockEditor(QWidget):
    """Editor that can switch between block editing and raw Markdown."""

    contentChanged = Signal()

    def __init__(self, markdown_text: str = "") -> None:
        super().__init__()
        self.setObjectName("MarkdownBlockEditor")
        self._original_source = markdown_text or ""
        self._changed_since_load = False
        self._suppress_change_signal = False
        self._raw_mode = False
        self._entries: list[dict[str, object]] = []

        try:
            self._blocks = parse_markdown_blocks(self._original_source)
            self._languages = collect_code_languages(self._blocks)
            parse_failed = False
        except MarkdownBlockParseError:
            self._blocks = [MarkdownBlock(kind="text", text="")]
            self._languages = list(DEFAULT_CODE_LANGUAGES)
            parse_failed = True

        self._build_ui()
        if parse_failed:
            self._show_raw_mode(parse_failed=True)
        else:
            self._show_block_mode()

    def to_markdown(self) -> str:
        """Return the current editor content as Markdown source."""
        if self._raw_mode:
            return self.raw_editor.toPlainText()
        if not self._changed_since_load:
            return self._original_source
        return serialize_markdown_blocks(self._read_blocks_from_entries())

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        toolbar = QFrame()
        toolbar.setObjectName("BlockEditorToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(10)

        self.add_text_button = QPushButton("添加文字块")
        self.add_text_button.setObjectName("SecondaryButton")
        self.add_text_button.clicked.connect(self.add_text_block)
        toolbar_layout.addWidget(self.add_text_button)

        self.add_code_button = QPushButton("添加代码块")
        self.add_code_button.setObjectName("SecondaryButton")
        self.add_code_button.clicked.connect(self.add_code_block)
        toolbar_layout.addWidget(self.add_code_button)

        self.toggle_mode_button = QPushButton("切换原始 Markdown")
        self.toggle_mode_button.setObjectName("SecondaryButton")
        self.toggle_mode_button.clicked.connect(self.toggle_mode)
        toolbar_layout.addWidget(self.toggle_mode_button)
        toolbar_layout.addStretch(1)
        layout.addWidget(toolbar)

        self.notice_label = QLabel("")
        self.notice_label.setObjectName("RawModeNotice")
        self.notice_label.setWordWrap(True)
        layout.addWidget(self.notice_label)

        self.blocks_container = QWidget()
        self.blocks_container.setObjectName("BlockEditorBlocks")
        self.blocks_layout = QVBoxLayout(self.blocks_container)
        self.blocks_layout.setContentsMargins(0, 0, 0, 0)
        self.blocks_layout.setSpacing(12)
        layout.addWidget(self.blocks_container)

        self.raw_editor = QTextEdit()
        self.raw_editor.setObjectName("EditorTextArea")
        self.raw_editor.setPlaceholderText("在这里输入 Markdown 原文...")
        self.raw_editor.setMinimumHeight(320)
        self.raw_editor.textChanged.connect(self._mark_changed)
        layout.addWidget(self.raw_editor, 1)

    def add_text_block(self) -> None:
        blocks = self._read_blocks_from_entries()
        blocks.append(MarkdownBlock(kind="text", text=""))
        self._replace_blocks(blocks, changed=True)

    def add_code_block(self) -> None:
        blocks = self._read_blocks_from_entries()
        blocks.append(MarkdownBlock(kind="code", text="", language="text"))
        self._replace_blocks(blocks, changed=True)

    def toggle_mode(self) -> None:
        if self._raw_mode:
            self._try_switch_to_blocks()
        else:
            self._show_raw_mode(source=self.to_markdown())

    def _show_block_mode(self) -> None:
        self._raw_mode = False
        self.notice_label.setVisible(False)
        self.blocks_container.setVisible(True)
        self.raw_editor.setVisible(False)
        self.add_text_button.setEnabled(True)
        self.add_code_button.setEnabled(True)
        self.toggle_mode_button.setText("切换原始 Markdown")
        self._refresh_blocks()

    def _show_raw_mode(self, *, source: str | None = None, parse_failed: bool = False) -> None:
        self._raw_mode = True
        self.blocks_container.setVisible(False)
        self.raw_editor.setVisible(True)
        self.add_text_button.setEnabled(False)
        self.add_code_button.setEnabled(False)
        self.toggle_mode_button.setText("切换块编辑")
        self.notice_label.setText(
            "无法安全解析为块，已保留原始 Markdown。"
            if parse_failed
            else "当前正在编辑原始 Markdown。"
        )
        self.notice_label.setVisible(True)

        self._suppress_change_signal = True
        self.raw_editor.setPlainText(self._original_source if source is None else source)
        self._suppress_change_signal = False

    def _try_switch_to_blocks(self) -> None:
        source = self.raw_editor.toPlainText()
        try:
            blocks = parse_markdown_blocks(source)
        except MarkdownBlockParseError:
            self.notice_label.setText("当前 Markdown 仍无法安全解析为块，请继续使用原始 Markdown。")
            self.notice_label.setVisible(True)
            return

        self._blocks = blocks
        self._languages = collect_code_languages(blocks)
        self._show_block_mode()

    def _replace_blocks(self, blocks: list[MarkdownBlock], *, changed: bool = False) -> None:
        self._blocks = blocks or [MarkdownBlock(kind="text", text="")]
        self._languages = collect_code_languages(self._blocks)
        self._refresh_blocks()
        if changed:
            self._mark_changed()

    def _refresh_blocks(self) -> None:
        self._clear_layout(self.blocks_layout)
        self._entries = []

        for index, block in enumerate(self._blocks):
            widget = self._build_block_widget(index, block)
            self.blocks_layout.addWidget(widget)

        self.blocks_layout.addStretch(1)

    def _build_block_widget(self, index: int, block: MarkdownBlock) -> QWidget:
        frame = QFrame()
        frame.setObjectName("TextBlockEditor" if block.kind == "text" else "CodeBlockEditor")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        title = QLabel("文字块" if block.kind == "text" else "代码块")
        title.setObjectName("BlockTitle")
        header.addWidget(title)
        header.addStretch(1)

        move_up = QPushButton("上移")
        move_up.setObjectName("BlockActionButton")
        move_up.setEnabled(index > 0)
        move_up.clicked.connect(lambda: self._move_block(index, -1))
        header.addWidget(move_up)

        move_down = QPushButton("下移")
        move_down.setObjectName("BlockActionButton")
        move_down.setEnabled(index < len(self._blocks) - 1)
        move_down.clicked.connect(lambda: self._move_block(index, 1))
        header.addWidget(move_down)

        delete_button = QPushButton("删除")
        delete_button.setObjectName("BlockDeleteButton")
        delete_button.clicked.connect(lambda: self._delete_block(index))
        header.addWidget(delete_button)
        layout.addLayout(header)

        entry: dict[str, object] = {"kind": block.kind}
        if block.kind == "code":
            language = QComboBox()
            language.setObjectName("BlockLanguageSelect")
            language.setEditable(True)
            language.addItems(self._language_options(block.language))
            self._set_combo_text(language, block.language or "text")
            language.currentTextChanged.connect(self._mark_changed)
            layout.addWidget(language)
            entry["language"] = language

            editor = QPlainTextEdit()
            editor.setObjectName("BlockCodeInput")
            editor.setPlainText(block.text)
            editor.setMinimumHeight(150)
            editor.textChanged.connect(self._mark_changed)
            layout.addWidget(editor)
            entry["editor"] = editor
        else:
            editor = QTextEdit()
            editor.setObjectName("BlockTextInput")
            editor.setPlainText(block.text)
            editor.setMinimumHeight(132)
            editor.textChanged.connect(self._mark_changed)
            layout.addWidget(editor)
            entry["editor"] = editor

        self._entries.append(entry)
        return frame

    def _move_block(self, index: int, offset: int) -> None:
        blocks = self._read_blocks_from_entries()
        target = index + offset
        if target < 0 or target >= len(blocks):
            return
        blocks[index], blocks[target] = blocks[target], blocks[index]
        self._replace_blocks(blocks, changed=True)

    def _delete_block(self, index: int) -> None:
        blocks = self._read_blocks_from_entries()
        if index < 0 or index >= len(blocks):
            return
        del blocks[index]
        if not blocks:
            blocks = [MarkdownBlock(kind="text", text="")]
        self._replace_blocks(blocks, changed=True)

    def _read_blocks_from_entries(self) -> list[MarkdownBlock]:
        blocks: list[MarkdownBlock] = []
        for entry in self._entries:
            kind = str(entry["kind"])
            editor = entry["editor"]
            if isinstance(editor, QTextEdit):
                text = editor.toPlainText()
            elif isinstance(editor, QPlainTextEdit):
                text = editor.toPlainText()
            else:
                text = ""

            language = ""
            combo = entry.get("language")
            if isinstance(combo, QComboBox):
                language = combo.currentText().strip() or "text"

            blocks.append(MarkdownBlock(kind=kind, text=text, language=language))
        return blocks

    def _mark_changed(self) -> None:
        if self._suppress_change_signal:
            return
        self._changed_since_load = True
        self.contentChanged.emit()

    def _language_options(self, current_language: str) -> list[str]:
        options = list(self._languages)
        current = current_language.strip()
        if current and current not in options:
            options.append(current)
        return options

    def _set_combo_text(self, combo: QComboBox, value: str) -> None:
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.setEditText(value)

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self._clear_child_layout(child_layout)

    def _clear_child_layout(self, layout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self._clear_child_layout(child_layout)
