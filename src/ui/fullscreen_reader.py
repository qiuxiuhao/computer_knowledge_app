"""Full-screen read-only Markdown reader."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
)

from src.models.card import Card
from src.ui.markdown_reader import MarkdownReaderWidget


class FullScreenReaderDialog(QDialog):
    """Large read-only dialog for focused card reading."""

    def __init__(self, card: Card, parent=None) -> None:
        super().__init__(parent)
        self.card = card
        self.setObjectName("FullScreenReader")
        self.setWindowTitle(card.title)
        self.resize(1280, 860)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        toolbar = QFrame()
        toolbar.setObjectName("FullScreenToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(42, 0, 42, 0)
        toolbar_layout.setSpacing(14)

        title = QLabel(card.title)
        title.setObjectName("FullScreenTitle")
        title.setWordWrap(False)
        toolbar_layout.addWidget(title, 1)

        self.copy_status = QLabel("")
        self.copy_status.setObjectName("CopyStatus")
        toolbar_layout.addWidget(self.copy_status)

        close_button = QPushButton("退出全屏")
        close_button.setObjectName("SecondaryButton")
        close_button.clicked.connect(self.close)
        toolbar_layout.addWidget(close_button)
        root.addWidget(toolbar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QFrame()
        content.setObjectName("FullScreenContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(72, 46, 72, 56)
        content_layout.setSpacing(0)
        content_layout.addWidget(MarkdownReaderWidget(card.content, self.show_copy_success))
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

    def show_copy_success(self) -> None:
        self.copy_status.setText("已复制代码")
        QTimer.singleShot(1500, lambda: self.copy_status.setText(""))

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if event.key() == Qt.Key_Escape:
            self.close()
            return
        super().keyPressEvent(event)

