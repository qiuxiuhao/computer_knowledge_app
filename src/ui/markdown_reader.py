"""Reusable Markdown reading widgets with copyable fenced code blocks."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from src.utils.markdown_renderer import (
    MarkdownSegment,
    parse_markdown_segments,
    render_markdown_to_html,
)


class MarkdownTextBlock(QTextBrowser):
    """Auto-height HTML block used inside the app's outer scroll area."""

    def __init__(self, markdown_text: str) -> None:
        super().__init__()
        self.setObjectName("MarkdownTextBlock")
        self.setFrameShape(QFrame.NoFrame)
        self.setOpenExternalLinks(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHtml(render_markdown_to_html(markdown_text))
        self.document().documentLayout().documentSizeChanged.connect(self._fit_to_document)
        self._fit_to_document(self.document().size())

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self.document().setTextWidth(self.viewport().width())
        self._fit_to_document(self.document().size())

    def _fit_to_document(self, size) -> None:
        self.setFixedHeight(max(28, int(size.height()) + 12))


class CodeBlockWidget(QFrame):
    """Fenced code block with a language label and one-click copy."""

    def __init__(
        self,
        segment: MarkdownSegment,
        on_copy_success: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self.code = segment.text
        self.on_copy_success = on_copy_success
        self.setObjectName("CopyableCodeBlock")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("CodeBlockHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(14, 0, 10, 0)
        header_layout.setSpacing(10)

        language = QLabel(segment.language or "code")
        language.setObjectName("CodeBlockLanguage")
        header_layout.addWidget(language)
        header_layout.addStretch(1)

        copy_button = QPushButton("复制")
        copy_button.setObjectName("CodeCopyButton")
        copy_button.clicked.connect(self.copy_code)
        header_layout.addWidget(copy_button)
        layout.addWidget(header)

        code_view = QPlainTextEdit()
        code_view.setObjectName("CodeBlockText")
        code_view.setPlainText(self.code)
        code_view.setReadOnly(True)
        code_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        code_view.setLineWrapMode(QPlainTextEdit.NoWrap)
        code_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        code_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        code_height = self._code_view_height()
        code_view.setFixedHeight(code_height)
        layout.addWidget(code_view)
        self.setFixedHeight(42 + code_height)

    def copy_code(self) -> None:
        QApplication.clipboard().setText(self.code)
        if self.on_copy_success is not None:
            self.on_copy_success()

    def _code_view_height(self) -> int:
        line_count = max(1, self.code.count("\n") + 1)
        natural_height = 22 * line_count + 24
        return min(max(natural_height, 82), 420)


class MarkdownReaderWidget(QWidget):
    """Read-only Markdown view that renders fenced code blocks as widgets."""

    def __init__(
        self,
        markdown_text: str,
        on_copy_success: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("MarkdownReader")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        for segment in parse_markdown_segments(markdown_text):
            if segment.kind == "code":
                layout.addWidget(CodeBlockWidget(segment, on_copy_success))
            elif segment.text:
                layout.addWidget(MarkdownTextBlock(segment.text))
            else:
                empty = MarkdownTextBlock("暂无正文内容。")
                layout.addWidget(empty)
