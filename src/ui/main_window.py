"""PySide6 main window connected to the SQLite cards table."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QCompleter,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.db.database import DEFAULT_DB_PATH, initialize_database
from src.models.card import Card
from src.services.card_service import (
    create_card,
    create_draft_card,
    delete_card,
    ensure_sample_data_if_empty,
    get_card_by_id,
    get_all_draft_cards,
    get_all_formal_cards,
    get_tag_suggestions,
    search_cards,
    update_card,
)
from src.ui.mock_data import CATEGORIES
from src.ui.fullscreen_reader import FullScreenReaderDialog
from src.ui.markdown_reader import MarkdownReaderWidget
from src.ui.styles import APP_STYLE
from src.utils.markdown_normalizer import normalize_markdown

SCENARIOS = [
    "知识点",
    "问题解决",
    "工作流",
    "常用命令",
    "项目经验",
    "软件技巧",
    "论文笔记",
    "其他",
]

CATEGORY_NAMES = [name for name, _count in CATEGORIES]
EDITOR_CATEGORIES = [
    "Python",
    "深度学习",
    "PyTorch",
    "AutoDL",
    "Mac",
    "Linux",
    "Conda",
    "Git",
    "常用命令",
    "报错解决",
    "项目经验",
    "论文笔记",
    "其他",
]


class EditorComboBox(QComboBox):
    """Editable combo box with an always-visible dropdown chevron."""

    def paintEvent(self, event) -> None:  # type: ignore[override]
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#2563EB"))
        pen.setWidthF(2.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        center_x = self.width() - 20
        center_y = self.height() // 2 + 1
        painter.drawLine(center_x - 5, center_y - 3, center_x, center_y + 2)
        painter.drawLine(center_x, center_y + 2, center_x + 5, center_y - 3)


class CollapseArrowLabel(QLabel):
    """Small painted chevron for collapsible sidebar sections."""

    def __init__(self) -> None:
        super().__init__()
        self.expanded = False
        self.setFixedSize(22, 22)

    def set_expanded(self, expanded: bool) -> None:
        self.expanded = expanded
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#2563EB"))
        pen.setWidthF(2.4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        center_x = self.width() // 2
        center_y = self.height() // 2
        if self.expanded:
            painter.drawLine(center_x - 5, center_y - 3, center_x, center_y + 3)
            painter.drawLine(center_x, center_y + 3, center_x + 5, center_y - 3)
        else:
            painter.drawLine(center_x - 3, center_y - 5, center_x + 3, center_y)
            painter.drawLine(center_x + 3, center_y, center_x - 3, center_y + 5)


class MainWindow(QMainWindow):
    """Main window for the local knowledge base."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        super().__init__()
        self.db_path = Path(db_path)
        initialize_database(self.db_path)
        ensure_sample_data_if_empty(self.db_path)

        self.all_formal_cards: list[Card] = []
        self.cards: list[Card] = []
        self.drafts: list[Card] = []
        self.selected_card_id: int | None = None
        self.selected_category = "全部"
        self.search_keyword = ""
        self.active_draft_editor_id: int | None = None
        self.card_widgets: dict[int, QFrame] = {}
        self.categories_collapsed = True
        self.drafts_collapsed = True
        self.search_input = QLineEdit()
        self.fullscreen_reader: FullScreenReaderDialog | None = None
        self.current_editor_card: Card | None = None
        self.current_editor_dirty = False
        self.editor_fields: dict[str, QWidget] = {}
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.setInterval(2000)
        self.autosave_timer.timeout.connect(self.flush_draft_autosave)

        self.setWindowTitle("个人计算机知识库")
        self.resize(1440, 900)
        self.setMinimumSize(1100, 720)
        self.setStyleSheet(APP_STYLE)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._build_top_bar())
        root_layout.addWidget(self._build_main_area(), 1)
        self.setCentralWidget(root)

        self.reload_data(select_first=True)

    def reload_data(self, select_first: bool = False, selected_card_id: int | None = None) -> None:
        self.all_formal_cards = get_all_formal_cards(self.db_path)
        self.drafts = get_all_draft_cards(self.db_path)
        self.cards = search_cards(
            self.search_keyword,
            category=self.selected_category,
            db_path=self.db_path,
        )

        if selected_card_id is not None:
            self.selected_card_id = selected_card_id
        elif select_first and self.cards:
            self.selected_card_id = self.cards[0].id
        elif self.selected_card_id not in {card.id for card in self.cards}:
            self.selected_card_id = self.cards[0].id if self.cards else None

        self._refresh_categories()
        self._refresh_drafts()
        self._refresh_card_list()
        self._show_selected_card()

    def _build_top_bar(self) -> QWidget:
        top_bar = QFrame()
        top_bar.setObjectName("TopBar")
        top_bar.setFixedHeight(68)

        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(34, 0, 28, 0)
        layout.setSpacing(18)

        app_name = QLabel("个人计算机知识库")
        app_name.setObjectName("AppName")
        layout.addWidget(app_name)

        layout.addSpacing(42)

        current_page = QLabel("知识库")
        current_page.setObjectName("CurrentPage")
        current_page.setAlignment(Qt.AlignCenter)
        layout.addWidget(current_page)

        layout.addSpacing(34)

        import_button = QPushButton("导入")
        import_button.setObjectName("SecondaryButton")
        import_button.setToolTip("导入功能将在后续版本支持")
        layout.addStretch(1)
        layout.addWidget(import_button)

        return top_bar

    def _build_main_area(self) -> QWidget:
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_sidebar())
        splitter.addWidget(self._build_detail_pane())
        splitter.setSizes([420, 1020])
        splitter.setHandleWidth(1)
        return splitter

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("UnifiedSidebar")
        sidebar.setMinimumWidth(360)
        sidebar.setMaximumWidth(520)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 20, 20, 22)
        layout.setSpacing(12)

        self.search_input.setObjectName("SearchBox")
        self.search_input.setPlaceholderText("搜索标题、标签、正文...")
        self.search_input.setClearButtonEnabled(False)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self.search_input)

        new_card = QPushButton("+  新建卡片")
        new_card.setObjectName("PrimaryButton")
        new_card.clicked.connect(self.show_new_card_editor)
        layout.addWidget(new_card)

        self.category_toggle_label = CollapseArrowLabel()
        self.category_toggle_label.setObjectName("CollapseArrow")
        self.category_header = self._build_collapse_header(
            "分类",
            self.category_toggle_label,
            self.toggle_categories,
        )
        layout.addWidget(self.category_header)

        self.category_container = QWidget()
        self.category_layout = QVBoxLayout(self.category_container)
        self.category_layout.setContentsMargins(0, 0, 0, 0)
        self.category_layout.setSpacing(7)
        self.category_scroll = QScrollArea()
        self.category_scroll.setObjectName("CategoryScroll")
        self.category_scroll.setWidgetResizable(True)
        self.category_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.category_scroll.setMaximumHeight(286)
        self.category_scroll.setWidget(self.category_container)
        layout.addWidget(self.category_scroll)

        divider = QFrame()
        divider.setObjectName("Divider")
        layout.addWidget(divider)

        self.draft_toggle_label = CollapseArrowLabel()
        self.draft_toggle_label.setObjectName("CollapseArrow")
        self.draft_count_label = QLabel("0")
        self.draft_count_label.setObjectName("SectionCount")
        self.draft_count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.draft_header = self._build_collapse_header(
            "草稿",
            self.draft_toggle_label,
            self.toggle_drafts,
            count_label=self.draft_count_label,
        )
        layout.addWidget(self.draft_header)

        self.draft_section = QWidget()
        draft_section_layout = QVBoxLayout(self.draft_section)
        draft_section_layout.setContentsMargins(0, 0, 0, 0)
        draft_section_layout.setSpacing(10)

        draft_input_row = QHBoxLayout()
        draft_input_row.setContentsMargins(0, 0, 0, 0)
        draft_input_row.setSpacing(8)

        self.draft_input = QLineEdit()
        self.draft_input.setObjectName("DraftInput")
        self.draft_input.setPlaceholderText("快速记下一个标题...")
        self.draft_input.returnPressed.connect(self.create_draft_from_input)
        draft_input_row.addWidget(self.draft_input, 1)

        add_draft_button = QPushButton("+")
        add_draft_button.setObjectName("DraftAddButton")
        add_draft_button.setToolTip("添加草稿")
        add_draft_button.clicked.connect(self.create_draft_from_input)
        draft_input_row.addWidget(add_draft_button)

        draft_section_layout.addLayout(draft_input_row)

        self.draft_container = QWidget()
        self.draft_layout = QVBoxLayout(self.draft_container)
        self.draft_layout.setContentsMargins(0, 0, 0, 0)
        self.draft_layout.setSpacing(8)
        draft_section_layout.addWidget(self.draft_container)
        layout.addWidget(self.draft_section)

        card_divider = QFrame()
        card_divider.setObjectName("Divider")
        layout.addWidget(card_divider)

        header = QHBoxLayout()
        self.card_list_title = QLabel("知识卡片")
        self.card_list_title.setObjectName("SectionTitle")
        self.card_count_label = QLabel("共 0 条")
        self.card_count_label.setObjectName("SectionCount")
        header.addWidget(self.card_list_title)
        header.addSpacing(12)
        header.addWidget(self.card_count_label)
        header.addStretch(1)
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.card_list_content = QWidget()
        self.card_list_layout = QVBoxLayout(self.card_list_content)
        self.card_list_layout.setContentsMargins(0, 0, 0, 0)
        self.card_list_layout.setSpacing(12)
        scroll.setWidget(self.card_list_content)
        layout.addWidget(scroll, 1)

        self._sync_collapsible_visibility()

        return sidebar

    def _build_collapse_header(
        self,
        title_text: str,
        arrow_label: QLabel,
        on_click: Callable[[], None],
        *,
        count_label: QLabel | None = None,
    ) -> QWidget:
        header = QFrame()
        header.setObjectName("CollapseHeader")
        header.setCursor(Qt.PointingHandCursor)
        header.mousePressEvent = lambda _event: on_click()  # type: ignore[method-assign]

        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(8)

        title = QLabel(title_text)
        title.setObjectName("SectionTitle")
        layout.addWidget(title)
        if count_label is not None:
            layout.addWidget(count_label)
        layout.addStretch(1)
        layout.addWidget(arrow_label)

        return header

    def toggle_categories(self) -> None:
        self.categories_collapsed = not self.categories_collapsed
        self._sync_collapsible_visibility()

    def toggle_drafts(self) -> None:
        self.drafts_collapsed = not self.drafts_collapsed
        self._sync_collapsible_visibility()

    def _sync_collapsible_visibility(self) -> None:
        if hasattr(self, "category_scroll"):
            self.category_scroll.setVisible(not self.categories_collapsed)
        if hasattr(self, "category_container"):
            self.category_container.setVisible(not self.categories_collapsed)
        if hasattr(self, "draft_section"):
            self.draft_section.setVisible(not self.drafts_collapsed)
        if hasattr(self, "category_toggle_label"):
            self.category_toggle_label.set_expanded(not self.categories_collapsed)
        if hasattr(self, "draft_toggle_label"):
            self.draft_toggle_label.set_expanded(not self.drafts_collapsed)

    def _build_detail_pane(self) -> QWidget:
        pane = QFrame()
        pane.setObjectName("DetailPane")
        pane.setMinimumWidth(520)

        outer = QVBoxLayout(pane)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        toolbar = QFrame()
        toolbar.setObjectName("DetailToolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(40, 0, 48, 0)
        toolbar_layout.setSpacing(12)

        self.detail_mode_label = QLabel("知识卡片")
        self.detail_mode_label.setObjectName("DetailModeLabel")
        toolbar_layout.addWidget(self.detail_mode_label)
        self.autosave_status_label = QLabel("")
        self.autosave_status_label.setObjectName("AutosaveStatus")
        toolbar_layout.addWidget(self.autosave_status_label)
        toolbar_layout.addStretch(1)

        self.detail_action_container = QWidget()
        self.detail_action_layout = QHBoxLayout(self.detail_action_container)
        self.detail_action_layout.setContentsMargins(0, 0, 0, 0)
        self.detail_action_layout.setSpacing(10)
        toolbar_layout.addWidget(self.detail_action_container)

        outer.addWidget(toolbar)

        self.detail_scroll = QScrollArea()
        self.detail_scroll.setWidgetResizable(True)
        self.detail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        outer.addWidget(self.detail_scroll, 1)

        return pane

    def _refresh_categories(self) -> None:
        self._clear_layout(self.category_layout)
        counts: dict[str, int] = {name: 0 for name in CATEGORY_NAMES}
        counts["全部"] = len(self.all_formal_cards)
        for card in self.all_formal_cards:
            if card.category in counts:
                counts[card.category] += 1

        for name in CATEGORY_NAMES:
            selected = name == self.selected_category
            self.category_layout.addWidget(self._build_category_row(name, counts.get(name, 0), selected))
        self._sync_collapsible_visibility()

    def _refresh_drafts(self) -> None:
        self._clear_layout(self.draft_layout)
        self.draft_count_label.setText(str(len(self.drafts)))

        if not self.drafts:
            empty = QLabel("暂无草稿")
            empty.setObjectName("MutedText")
            self.draft_layout.addWidget(empty)
            self._sync_collapsible_visibility()
            return

        for draft in self.drafts:
            self.draft_layout.addWidget(self._build_draft_row(draft))
        self._sync_collapsible_visibility()

    def _refresh_card_list(self) -> None:
        self._clear_layout(self.card_list_layout)
        self.card_widgets.clear()
        self.card_list_title.setText("搜索结果" if self.search_keyword else "知识卡片")
        self.card_count_label.setText(f"共 {len(self.cards)} 条")

        if not self.cards:
            if self.search_keyword:
                message = "没有找到相关知识卡片"
            elif self.selected_category != "全部":
                message = f"“{self.selected_category}”分类下还没有知识卡片。"
            else:
                message = "还没有知识卡片\n点击“新建卡片”开始记录你的第一个知识点。"
            empty = QLabel(message)
            empty.setObjectName("MutedText")
            empty.setWordWrap(True)
            self.card_list_layout.addWidget(empty)
            self.card_list_layout.addStretch(1)
            return

        for card in self.cards:
            selected = card.id == self.selected_card_id
            item = self._build_card_item(card, selected=selected)
            self.card_widgets[int(card.id)] = item
            self.card_list_layout.addWidget(item)
        self.card_list_layout.addStretch(1)

    def _build_category_row(self, name: str, count: int, selected: bool = False) -> QWidget:
        row = QFrame()
        row.setObjectName("CategoryRow")
        row.setProperty("selected", "true" if selected else "false")
        row.setCursor(Qt.PointingHandCursor)
        row.setFixedHeight(38)
        row.mousePressEvent = self._make_category_click_handler(name)  # type: ignore[method-assign]

        layout = QHBoxLayout(row)
        layout.setContentsMargins(9, 0, 10, 0)
        layout.setSpacing(10)

        icon = QLabel(self._category_marker(name))
        icon.setObjectName("CategoryIcon")
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)

        label = QLabel(name)
        label.setObjectName("CategoryName")
        layout.addWidget(label, 1)

        count_label = QLabel(str(count))
        count_label.setObjectName("CategoryCount")
        count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(count_label)

        return row

    def _build_draft_row(self, draft: Card) -> QWidget:
        row = QFrame()
        row.setObjectName("DraftRow")
        row.setCursor(Qt.PointingHandCursor)
        row.mousePressEvent = self._make_draft_click_handler(draft.id)  # type: ignore[method-assign]
        layout = QHBoxLayout(row)
        layout.setContentsMargins(8, 0, 4, 0)
        layout.setSpacing(8)

        icon = QLabel("□")
        icon.setObjectName("DraftIcon")
        layout.addWidget(icon)

        label = QLabel(draft.title)
        label.setObjectName("DraftTitle")
        label.setWordWrap(False)
        layout.addWidget(label, 1)

        delete_button = QPushButton("删除")
        delete_button.setObjectName("DraftDeleteButton")
        delete_button.clicked.connect(lambda: self.confirm_delete_draft(draft))
        layout.addWidget(delete_button)

        return row

    def _build_card_item(self, card: Card, selected: bool = False) -> QWidget:
        item = QFrame()
        item.setObjectName("CardItem")
        item.setProperty("selected", "true" if selected else "false")
        item.setCursor(Qt.PointingHandCursor)
        item.mousePressEvent = self._make_card_click_handler(card.id)  # type: ignore[method-assign]

        layout = QVBoxLayout(item)
        layout.setContentsMargins(18, 16, 18, 14)
        layout.setSpacing(10)

        title = QLabel(card.title)
        title.setObjectName("CardTitle")
        title.setWordWrap(True)
        layout.addWidget(title)

        summary_text = card.summary or "暂无一句话总结"
        summary = QLabel(summary_text)
        summary.setObjectName("CardSummary")
        summary.setWordWrap(True)
        layout.addWidget(summary)

        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(8)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        for tag in self._split_tags(card.tags)[:4]:
            tag_label = QLabel(tag)
            tag_label.setObjectName("TagPill")
            tags_layout.addWidget(tag_label)
        tags_layout.addStretch(1)
        layout.addLayout(tags_layout)

        meta_layout = QHBoxLayout()
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(4)
        category = card.category or "未分类"
        scenario = card.scenario or "未填写"
        left_meta = QLabel(f"{category} · {scenario}")
        left_meta.setObjectName("CardMeta")
        right_meta = QLabel(f"更新于 {card.updated_at}")
        right_meta.setObjectName("CardMeta")
        right_meta.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        meta_layout.addWidget(left_meta)
        meta_layout.addStretch(1)
        meta_layout.addWidget(right_meta)
        layout.addLayout(meta_layout)

        return item

    def _make_card_click_handler(self, card_id: int | None) -> Callable:
        def handle_click(_event) -> None:
            if card_id is not None:
                self.select_card(card_id)

        return handle_click

    def _make_category_click_handler(self, category: str) -> Callable:
        def handle_click(_event) -> None:
            self.select_category(category)

        return handle_click

    def _make_draft_click_handler(self, card_id: int | None) -> Callable:
        def handle_click(_event) -> None:
            if card_id is not None:
                self.open_draft_editor(card_id)

        return handle_click

    def select_category(self, category: str) -> None:
        if category == self.selected_category:
            return
        if not self.flush_pending_editor_changes():
            return
        self.active_draft_editor_id = None
        self.selected_category = category
        self.selected_card_id = None
        self.reload_data(select_first=True)

    def on_search_text_changed(self, text: str) -> None:
        if not self.flush_pending_editor_changes():
            self.search_input.blockSignals(True)
            self.search_input.setText(self.search_keyword)
            self.search_input.blockSignals(False)
            return
        self.active_draft_editor_id = None
        self.search_keyword = text.strip()
        self.selected_card_id = None
        self.reload_data(select_first=True)

    def select_card(self, card_id: int) -> None:
        if not self.flush_pending_editor_changes():
            return
        self.active_draft_editor_id = None
        self.selected_card_id = card_id
        for existing_id, widget in self.card_widgets.items():
            self._set_selected_property(widget, existing_id == card_id)
        self._show_selected_card()

    def _show_selected_card(self) -> None:
        card = self._selected_card()
        if card is None:
            self._set_detail_widget(self._build_empty_detail())
            return
        self._set_detail_widget(self._build_preview_detail(card))

    def show_new_card_editor(self) -> None:
        if not self.flush_pending_editor_changes():
            return
        draft = create_draft_card("未命名草稿", db_path=self.db_path)
        self.active_draft_editor_id = None
        self.selected_card_id = None
        for widget in self.card_widgets.values():
            self._set_selected_property(widget, False)
        self.reload_data(selected_card_id=self.selected_card_id)
        self.open_draft_editor(int(draft.id))

    def show_edit_card_editor(self, card: Card) -> None:
        if not self.flush_pending_editor_changes():
            return
        self.active_draft_editor_id = None
        self._set_detail_widget(self._build_edit_detail(card=card))

    def open_draft_editor(self, card_id: int) -> None:
        if not self.flush_pending_editor_changes():
            return
        draft = get_card_by_id(card_id, self.db_path)
        if draft is None or draft.is_draft != 1:
            self.reload_data(select_first=True)
            return

        self.selected_card_id = None
        self.active_draft_editor_id = card_id
        for widget in self.card_widgets.values():
            self._set_selected_property(widget, False)
        self._set_detail_widget(self._build_edit_detail(card=draft))

    def create_draft_from_input(self) -> None:
        if not self.flush_pending_editor_changes():
            return
        title = self.draft_input.text().strip()
        if not title:
            return

        create_draft_card(title, db_path=self.db_path)
        self.draft_input.clear()
        self.reload_data(selected_card_id=self.selected_card_id)

    def save_editor(self, card: Card | None, fields: dict[str, str]) -> None:
        title = fields["title"].strip()
        if not title:
            QMessageBox.warning(self, "无法保存", "标题不能为空。")
            return
        self.autosave_timer.stop()
        markdown_content = normalize_markdown(fields["content"])

        if card is None:
            saved = create_card(
                title=title,
                scenario=fields["scenario"],
                category=fields["category"],
                tags=fields["tags"],
                summary=fields["summary"],
                content=markdown_content,
                keywords=fields["keywords"],
                source=fields["source"],
                is_draft=0,
                db_path=self.db_path,
            )
        else:
            saved = update_card(
                int(card.id),
                db_path=self.db_path,
                title=title,
                scenario=fields["scenario"],
                category=fields["category"],
                tags=fields["tags"],
                summary=fields["summary"],
                content=markdown_content,
                keywords=fields["keywords"],
                source=fields["source"],
                is_draft=0,
            )

        if saved is None:
            QMessageBox.warning(self, "保存失败", "没有找到要更新的知识卡片。")
            self.reload_data(select_first=True)
            return

        if card is not None and card.is_draft == 1:
            self.active_draft_editor_id = None
            self.selected_category = "全部"
            self.search_keyword = ""
            self.search_input.blockSignals(True)
            self.search_input.clear()
            self.search_input.blockSignals(False)

        self.reload_data(selected_card_id=saved.id)

    def confirm_delete_card(self, card: Card) -> None:
        answer = QMessageBox.question(
            self,
            "删除知识卡片",
            f"确定删除这张知识卡片吗？\n\n{card.title}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return

        delete_card(int(card.id), self.db_path)
        self.selected_card_id = None
        self.reload_data(select_first=True)

    def confirm_delete_draft(self, draft: Card) -> None:
        answer = QMessageBox.question(
            self,
            "删除草稿",
            f"确定删除这个草稿吗？\n\n{draft.title}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return

        delete_card(int(draft.id), self.db_path)
        if self.active_draft_editor_id == draft.id:
            self.active_draft_editor_id = None
            self.reload_data(select_first=True)
        else:
            self.reload_data(selected_card_id=self.selected_card_id)

    def _build_preview_detail(self, card: Card) -> QWidget:
        self._reset_editor_state()
        self._set_detail_actions(
            "阅读模式",
            [
                ("全屏阅读", "SecondaryButton", lambda: self.open_fullscreen_reader(card)),
                ("编辑", "EditButton", lambda: self.show_edit_card_editor(card)),
                ("删除", "DeleteButton", lambda: self.confirm_delete_card(card)),
            ],
        )

        content = QWidget()
        content.setObjectName("DetailContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 44, 48, 40)
        layout.setSpacing(18)

        title = QLabel(card.title)
        title.setObjectName("DetailTitle")
        title.setWordWrap(True)
        layout.addWidget(title)

        layout.addSpacing(16)
        layout.addLayout(self._build_meta_row("用途场景：", card.scenario or "未填写"))
        layout.addLayout(self._build_meta_row("分类：", card.category or "未分类"))
        layout.addLayout(self._build_meta_row("标签：", self._format_tags(card.tags), link_style=True))
        layout.addLayout(self._build_meta_row("一句话总结：", card.summary or "暂无"))

        rule = QLabel()
        rule.setObjectName("HorizontalRule")
        layout.addSpacing(8)
        layout.addWidget(rule)
        layout.addSpacing(8)

        body_title = QLabel("正文内容")
        body_title.setObjectName("ArticleHeading")
        layout.addWidget(body_title)

        preview = MarkdownReaderWidget(card.content, self.show_code_copied)
        layout.addWidget(preview, 1)

        return content

    def open_fullscreen_reader(self, card: Card) -> None:
        self.fullscreen_reader = FullScreenReaderDialog(card, self)
        self.fullscreen_reader.showFullScreen()

    def show_code_copied(self) -> None:
        self.statusBar().showMessage("已复制代码", 1500)

    def _build_edit_detail(self, card: Card | None) -> QWidget:
        self.current_editor_card = card
        self.current_editor_dirty = False
        self.editor_fields = {}
        content = QWidget()
        content.setObjectName("DetailContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 34, 48, 40)
        layout.setSpacing(14)

        if card is None:
            editor_title = "新建知识卡片"
        elif card.is_draft:
            editor_title = "补充草稿并保存为正式卡片"
        else:
            editor_title = "编辑知识卡片"

        title = QLabel(editor_title)
        title.setObjectName("DetailTitle")
        layout.addWidget(title)

        title_input = QLineEdit(card.title if card else "")
        title_input.setObjectName("EditorInput")
        title_input.setPlaceholderText("标题")
        layout.addWidget(self._build_editor_field("标题", title_input))

        scenario_input = EditorComboBox()
        scenario_input.setObjectName("EditorInput")
        scenario_input.setEditable(True)
        scenario_input.addItems(SCENARIOS)
        self._set_combo_text(scenario_input, card.scenario if card else "知识点")

        category_input = EditorComboBox()
        category_input.setObjectName("EditorInput")
        category_input.setEditable(True)
        category_input.addItems(EDITOR_CATEGORIES)
        category_completer = QCompleter(EDITOR_CATEGORIES, category_input)
        category_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        category_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        category_input.setCompleter(category_completer)
        self._set_combo_text(category_input, card.category if card else "深度学习")

        tags_input = QLineEdit(card.tags if card else "")
        tags_input.setObjectName("EditorInput")
        tags_input.setPlaceholderText("例如：MLP, PyTorch, 神经网络")
        tag_completer = QCompleter(get_tag_suggestions(self.db_path), tags_input)
        tag_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        tag_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        tags_input.setCompleter(tag_completer)

        keywords_input = QLineEdit(card.keywords if card else "")
        keywords_input.setObjectName("EditorInput")
        keywords_input.setPlaceholderText("用于搜索的额外关键词")

        source_input = QLineEdit(card.source if card else "")
        source_input.setObjectName("EditorInput")
        source_input.setPlaceholderText("来源链接或来源说明")

        summary_input = QLineEdit(card.summary if card else "")
        summary_input.setObjectName("EditorInput")
        summary_input.setPlaceholderText("一句话总结")

        layout.addWidget(
            self._build_editor_two_column_row(
                self._build_editor_field("用途场景", scenario_input),
                self._build_editor_field("分类", category_input),
            )
        )
        layout.addWidget(
            self._build_editor_two_column_row(
                self._build_editor_field("标签", tags_input),
                self._build_editor_field("关键词", keywords_input),
            )
        )
        layout.addWidget(self._build_editor_field("来源", source_input))
        layout.addWidget(self._build_editor_field("一句话总结", summary_input))

        content_label = QLabel("Markdown 正文")
        content_label.setObjectName("MetaLabel")
        layout.addWidget(content_label)

        content_input = QTextEdit()
        content_input.setObjectName("EditorTextArea")
        content_input.setPlaceholderText("在这里输入 Markdown 原文...")
        content_input.setPlainText(card.content if card else "")
        content_input.setMinimumHeight(320)
        layout.addWidget(content_input, 1)

        self.editor_fields = {
            "title": title_input,
            "scenario": scenario_input,
            "category": category_input,
            "tags": tags_input,
            "summary": summary_input,
            "keywords": keywords_input,
            "source": source_input,
            "content": content_input,
        }
        self._connect_editor_change_signals()
        self.set_autosave_status("已自动保存" if card is not None and card.is_draft == 1 else "")

        self._set_detail_actions(
            "编辑模式",
            [
                ("保存", "PrimaryButton", lambda: self.save_editor(card, self.collect_editor_fields())),
                ("取消", "SecondaryButton", lambda: self.cancel_editor(card)),
            ],
        )

        return content

    def cancel_editor(self, card: Card | None) -> None:
        if card is not None and card.is_draft == 1:
            if not self.flush_draft_autosave():
                return
            self.active_draft_editor_id = None
            self.selected_card_id = None
            self._reset_editor_state()
            self._set_detail_widget(self._build_empty_detail())
            return

        if card is not None and card.is_draft == 0:
            self.selected_card_id = card.id
        self._reset_editor_state()
        self._show_selected_card()

    def _build_empty_detail(self) -> QWidget:
        self._reset_editor_state()
        self._set_detail_actions("知识卡片", [])
        content = QWidget()
        content.setObjectName("DetailContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 44, 48, 40)
        layout.setSpacing(16)
        message = QLabel("请选择一张知识卡片查看详情，或点击“新建卡片”开始记录。")
        message.setObjectName("MutedText")
        message.setWordWrap(True)
        layout.addWidget(message)
        layout.addStretch(1)
        return content

    def _build_meta_row(self, label_text: str, value_text: str, link_style: bool = False) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(14)
        label = QLabel(label_text)
        label.setObjectName("MetaLabel")
        row.addWidget(label)

        value = QLabel(value_text)
        value.setObjectName("MetaValueLink" if link_style else "MetaValue")
        value.setWordWrap(True)
        row.addWidget(value, 1)

        return row

    def _build_editor_field(self, label_text: str, field: QWidget) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        label = QLabel(label_text)
        label.setObjectName("MetaLabel")
        layout.addWidget(label)
        layout.addWidget(field)
        return wrapper

    def _build_editor_two_column_row(self, left: QWidget, right: QWidget) -> QWidget:
        wrapper = QWidget()
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        layout.addWidget(left, 1)
        layout.addWidget(right, 1)
        return wrapper

    def collect_editor_fields(self) -> dict[str, str]:
        fields: dict[str, str] = {}
        for name, widget in self.editor_fields.items():
            if isinstance(widget, QComboBox):
                fields[name] = widget.currentText().strip()
            elif isinstance(widget, QLineEdit):
                fields[name] = widget.text().strip()
            elif isinstance(widget, QTextEdit):
                fields[name] = widget.toPlainText()
        return fields

    def _connect_editor_change_signals(self) -> None:
        for widget in self.editor_fields.values():
            if isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(self.mark_editor_dirty)
            elif isinstance(widget, QLineEdit):
                widget.textChanged.connect(self.mark_editor_dirty)
            elif isinstance(widget, QTextEdit):
                widget.textChanged.connect(self.mark_editor_dirty)

    def mark_editor_dirty(self) -> None:
        if self.current_editor_card is None:
            return

        self.current_editor_dirty = True
        if self.current_editor_card.is_draft == 1:
            self.set_autosave_status("未保存")
            self.autosave_timer.start()
        else:
            self.set_autosave_status("未保存")

    def set_autosave_status(self, text: str) -> None:
        if hasattr(self, "autosave_status_label"):
            self.autosave_status_label.setText(text)

    def flush_draft_autosave(self) -> bool:
        card = self.current_editor_card
        if card is None or card.is_draft != 1:
            return True
        if not self.current_editor_dirty:
            return True

        self.autosave_timer.stop()
        fields = self.collect_editor_fields()
        title = fields["title"].strip() or "未命名草稿"
        markdown_content = normalize_markdown(fields["content"])

        try:
            saved = update_card(
                int(card.id),
                db_path=self.db_path,
                title=title,
                scenario=fields["scenario"],
                category=fields["category"],
                tags=fields["tags"],
                summary=fields["summary"],
                content=markdown_content,
                keywords=fields["keywords"],
                source=fields["source"],
                is_draft=1,
            )
        except Exception as error:
            self.set_autosave_status("自动保存失败")
            QMessageBox.warning(self, "自动保存失败", f"草稿自动保存失败：\n{error}")
            return False

        if saved is None:
            self.set_autosave_status("自动保存失败")
            QMessageBox.warning(self, "自动保存失败", "没有找到要自动保存的草稿。")
            return False

        self.current_editor_card = saved
        self.current_editor_dirty = False
        self.set_autosave_status("已自动保存")
        self.drafts = get_all_draft_cards(self.db_path)
        self._refresh_drafts()
        return True

    def flush_pending_editor_changes(self) -> bool:
        card = self.current_editor_card
        if card is None or not self.current_editor_dirty:
            return True

        if card.is_draft == 1:
            return self.flush_draft_autosave()

        answer = QMessageBox.question(
            self,
            "未保存的修改",
            "当前正式卡片有未保存的修改，是否保存？",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save,
        )
        if answer == QMessageBox.Cancel:
            return False
        if answer == QMessageBox.Discard:
            self._reset_editor_state()
            return True

        self.save_editor(card, self.collect_editor_fields())
        return True

    def _reset_editor_state(self) -> None:
        self.autosave_timer.stop()
        self.current_editor_card = None
        self.current_editor_dirty = False
        self.editor_fields = {}
        self.set_autosave_status("")

    def _set_detail_actions(
        self,
        mode_label: str,
        actions: list[tuple[str, str, Callable[[], None]]],
    ) -> None:
        self.detail_mode_label.setText(mode_label)
        self._clear_layout(self.detail_action_layout)

        for text, object_name, handler in actions:
            button = QPushButton(text)
            button.setObjectName(object_name)
            button.clicked.connect(handler)
            self.detail_action_layout.addWidget(button)

    def _set_detail_widget(self, widget: QWidget) -> None:
        old_widget = self.detail_scroll.takeWidget()
        if old_widget is not None:
            old_widget.deleteLater()
        self.detail_scroll.setWidget(widget)

    def _selected_card(self) -> Card | None:
        for card in self.cards:
            if card.id == self.selected_card_id:
                return card
        return None

    def _set_selected_property(self, widget: QWidget, selected: bool) -> None:
        widget.setProperty("selected", "true" if selected else "false")
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self._clear_layout(child_layout)

    def _set_combo_text(self, combo: QComboBox, value: str) -> None:
        if not value:
            return
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.setEditText(value)

    def _split_tags(self, tags: str) -> list[str]:
        return [tag.strip() for tag in tags.replace("，", ",").split(",") if tag.strip()]

    def _format_tags(self, tags: str) -> str:
        split_tags = self._split_tags(tags)
        return " / ".join(split_tags) if split_tags else "暂无"

    def _category_marker(self, name: str) -> str:
        markers = {
            "全部": "◆",
            "Python": "Py",
            "深度学习": "◎",
            "PyTorch": "Pt",
            "AutoDL": "☁",
            "Mac": "M",
            "Linux": "L",
            "Conda": "C",
            "Git": "G",
            "常用命令": ">_",
            "报错解决": "!",
            "项目经验": "P",
            "论文笔记": "N",
        }
        return markers.get(name, "•")

    def closeEvent(self, event) -> None:  # type: ignore[override]
        card = self.current_editor_card
        if card is not None and card.is_draft == 1 and self.current_editor_dirty:
            if self.flush_draft_autosave():
                event.accept()
                return

            answer = QMessageBox.question(
                self,
                "草稿尚未保存",
                "草稿自动保存失败，仍然要退出吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
            return

        if not self.flush_pending_editor_changes():
            event.ignore()
            return

        event.accept()
