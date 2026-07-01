"""PySide6 main window connected to the SQLite cards table."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.db.database import DEFAULT_DB_PATH, initialize_database
from src.models.card import Card
from src.services.card_service import (
    create_card,
    delete_card,
    ensure_sample_data_if_empty,
    get_card_by_id,
    get_all_draft_cards,
    get_all_formal_cards,
    search_cards,
    update_card,
)
from src.ui.mock_data import CATEGORIES
from src.ui.styles import APP_STYLE
from src.utils.markdown_renderer import render_markdown_to_html

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
        self.card_widgets: dict[int, QFrame] = {}

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

        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchBox")
        self.search_input.setPlaceholderText("搜索标题、标签、正文...")
        self.search_input.setClearButtonEnabled(False)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        layout.addWidget(self.search_input, 1)

        new_card = QPushButton("+  新建卡片")
        new_card.setObjectName("PrimaryButton")
        new_card.clicked.connect(self.show_new_card_editor)
        layout.addWidget(new_card)

        import_button = QPushButton("导入")
        import_button.setObjectName("SecondaryButton")
        import_button.setToolTip("导入功能将在后续版本支持")
        layout.addWidget(import_button)

        return top_bar

    def _build_main_area(self) -> QWidget:
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_sidebar())
        splitter.addWidget(self._build_card_list_pane())
        splitter.addWidget(self._build_detail_pane())
        splitter.setSizes([290, 390, 760])
        splitter.setHandleWidth(1)
        return splitter

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setMinimumWidth(250)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 24, 20, 28)
        layout.setSpacing(14)

        title = QLabel("分类")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        self.category_container = QWidget()
        self.category_layout = QVBoxLayout(self.category_container)
        self.category_layout.setContentsMargins(0, 0, 0, 0)
        self.category_layout.setSpacing(7)
        layout.addWidget(self.category_container, 1)

        divider = QFrame()
        divider.setObjectName("Divider")
        layout.addWidget(divider)

        draft_header = QHBoxLayout()
        draft_title = QLabel("草稿")
        draft_title.setObjectName("SectionTitle")
        self.draft_count_label = QLabel("0")
        self.draft_count_label.setObjectName("SectionCount")
        self.draft_count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        draft_header.addWidget(draft_title)
        draft_header.addStretch(1)
        draft_header.addWidget(self.draft_count_label)
        layout.addLayout(draft_header)

        draft_input = QLineEdit()
        draft_input.setObjectName("DraftInput")
        draft_input.setPlaceholderText("快速记下一个标题...")
        draft_input.setToolTip("草稿快速创建将在后续阶段实现")
        layout.addWidget(draft_input)

        self.draft_container = QWidget()
        self.draft_layout = QVBoxLayout(self.draft_container)
        self.draft_layout.setContentsMargins(0, 0, 0, 0)
        self.draft_layout.setSpacing(8)
        layout.addWidget(self.draft_container)

        return sidebar

    def _build_card_list_pane(self) -> QWidget:
        pane = QFrame()
        pane.setObjectName("ListPane")
        pane.setMinimumWidth(340)

        layout = QVBoxLayout(pane)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("知识卡片")
        title.setObjectName("SectionTitle")
        self.card_count_label = QLabel("共 0 条")
        self.card_count_label.setObjectName("SectionCount")
        header.addWidget(title)
        header.addSpacing(14)
        header.addWidget(self.card_count_label)
        header.addStretch(1)
        filter_label = QLabel("筛选")
        filter_label.setObjectName("MutedText")
        filter_label.setToolTip("分类过滤将在后续阶段完善")
        header.addWidget(filter_label)
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.card_list_content = QWidget()
        self.card_list_layout = QVBoxLayout(self.card_list_content)
        self.card_list_layout.setContentsMargins(0, 0, 0, 0)
        self.card_list_layout.setSpacing(14)
        scroll.setWidget(self.card_list_content)
        layout.addWidget(scroll, 1)

        return pane

    def _build_detail_pane(self) -> QWidget:
        pane = QFrame()
        pane.setObjectName("DetailPane")
        pane.setMinimumWidth(520)

        outer = QVBoxLayout(pane)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.detail_scroll = QScrollArea()
        self.detail_scroll.setWidgetResizable(True)
        self.detail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        outer.addWidget(self.detail_scroll)

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
        self.category_layout.addStretch(1)

    def _refresh_drafts(self) -> None:
        self._clear_layout(self.draft_layout)
        self.draft_count_label.setText(str(len(self.drafts)))

        if not self.drafts:
            empty = QLabel("暂无草稿")
            empty.setObjectName("MutedText")
            self.draft_layout.addWidget(empty)
            return

        for draft in self.drafts:
            self.draft_layout.addWidget(self._build_draft_row(draft))

    def _refresh_card_list(self) -> None:
        self._clear_layout(self.card_list_layout)
        self.card_widgets.clear()
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
        self.selected_category = category
        self.selected_card_id = None
        self.reload_data(select_first=True)

    def on_search_text_changed(self, text: str) -> None:
        self.search_keyword = text.strip()
        self.selected_card_id = None
        self.reload_data(select_first=True)

    def select_card(self, card_id: int) -> None:
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
        self.selected_card_id = None
        for widget in self.card_widgets.values():
            self._set_selected_property(widget, False)
        self._set_detail_widget(self._build_edit_detail(card=None))

    def show_edit_card_editor(self, card: Card) -> None:
        self._set_detail_widget(self._build_edit_detail(card=card))

    def open_draft_editor(self, card_id: int) -> None:
        draft = get_card_by_id(card_id, self.db_path)
        if draft is None or draft.is_draft != 1:
            self.reload_data(select_first=True)
            return

        self.selected_card_id = None
        for widget in self.card_widgets.values():
            self._set_selected_property(widget, False)
        self._set_detail_widget(self._build_edit_detail(card=draft))

    def save_editor(self, card: Card | None, fields: dict[str, str]) -> None:
        title = fields["title"].strip()
        if not title:
            QMessageBox.warning(self, "无法保存", "标题不能为空。")
            return

        if card is None:
            saved = create_card(
                title=title,
                scenario=fields["scenario"],
                category=fields["category"],
                tags=fields["tags"],
                summary=fields["summary"],
                content=fields["content"],
                keywords="",
                source="",
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
                content=fields["content"],
                is_draft=0,
            )

        if saved is None:
            QMessageBox.warning(self, "保存失败", "没有找到要更新的知识卡片。")
            self.reload_data(select_first=True)
            return

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

    def _build_preview_detail(self, card: Card) -> QWidget:
        content = QWidget()
        content.setObjectName("DetailContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 44, 48, 40)
        layout.setSpacing(18)

        top = QHBoxLayout()
        title = QLabel(card.title)
        title.setObjectName("DetailTitle")
        title.setWordWrap(True)
        top.addWidget(title, 1)

        edit_button = QPushButton("编辑")
        edit_button.setObjectName("EditButton")
        edit_button.clicked.connect(lambda: self.show_edit_card_editor(card))
        top.addWidget(edit_button)

        delete_button = QPushButton("删除")
        delete_button.setObjectName("DeleteButton")
        delete_button.clicked.connect(lambda: self.confirm_delete_card(card))
        top.addWidget(delete_button)
        layout.addLayout(top)

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

        preview = QTextBrowser()
        preview.setObjectName("PreviewBody")
        preview.setOpenExternalLinks(False)
        preview.setHtml(render_markdown_to_html(card.content))
        preview.setMinimumHeight(360)
        layout.addWidget(preview, 1)

        return content

    def _build_edit_detail(self, card: Card | None) -> QWidget:
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

        scenario_input = QComboBox()
        scenario_input.setObjectName("EditorInput")
        scenario_input.setEditable(True)
        scenario_input.addItems(SCENARIOS)
        self._set_combo_text(scenario_input, card.scenario if card else "知识点")
        layout.addWidget(self._build_editor_field("用途场景", scenario_input))

        category_input = QComboBox()
        category_input.setObjectName("EditorInput")
        category_input.setEditable(True)
        category_input.addItems([name for name in CATEGORY_NAMES if name != "全部"])
        self._set_combo_text(category_input, card.category if card else "深度学习")
        layout.addWidget(self._build_editor_field("分类", category_input))

        tags_input = QLineEdit(card.tags if card else "")
        tags_input.setObjectName("EditorInput")
        tags_input.setPlaceholderText("例如：MLP, PyTorch, 神经网络")
        layout.addWidget(self._build_editor_field("标签", tags_input))

        summary_input = QLineEdit(card.summary if card else "")
        summary_input.setObjectName("EditorInput")
        summary_input.setPlaceholderText("一句话总结")
        layout.addWidget(self._build_editor_field("一句话总结", summary_input))

        content_label = QLabel("Markdown 正文")
        content_label.setObjectName("MetaLabel")
        layout.addWidget(content_label)

        content_input = QTextEdit(card.content if card else "")
        content_input.setObjectName("EditorTextArea")
        content_input.setPlaceholderText("在这里输入 Markdown 原文...")
        content_input.setMinimumHeight(320)
        layout.addWidget(content_input, 1)

        actions = QHBoxLayout()
        actions.addStretch(1)
        save_button = QPushButton("保存")
        save_button.setObjectName("PrimaryButton")
        cancel_button = QPushButton("取消")
        cancel_button.setObjectName("SecondaryButton")
        actions.addWidget(save_button)
        actions.addWidget(cancel_button)
        layout.addLayout(actions)

        def collect_fields() -> dict[str, str]:
            return {
                "title": title_input.text(),
                "scenario": scenario_input.currentText().strip(),
                "category": category_input.currentText().strip(),
                "tags": tags_input.text().strip(),
                "summary": summary_input.text().strip(),
                "content": content_input.toPlainText(),
            }

        save_button.clicked.connect(lambda: self.save_editor(card, collect_fields()))
        cancel_button.clicked.connect(lambda: self.cancel_editor(card))

        return content

    def cancel_editor(self, card: Card | None) -> None:
        if card is not None and card.is_draft == 0:
            self.selected_card_id = card.id
        self._show_selected_card()

    def _build_empty_detail(self) -> QWidget:
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
