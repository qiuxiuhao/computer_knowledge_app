"""Static Stage 1 PySide6 main window."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.ui.mock_data import CARDS, CATEGORIES, DRAFTS, MLP_PREVIEW
from src.ui.styles import APP_STYLE


class MainWindow(QMainWindow):
    """A runnable static window with mock knowledge-base data."""

    def __init__(self) -> None:
        super().__init__()
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

        search = QLineEdit()
        search.setObjectName("SearchBox")
        search.setPlaceholderText("搜索标题、标签、正文...")
        search.setClearButtonEnabled(False)
        layout.addWidget(search, 1)

        new_card = QPushButton("+  新建卡片")
        new_card.setObjectName("PrimaryButton")
        layout.addWidget(new_card)

        import_button = QPushButton("导入")
        import_button.setObjectName("SecondaryButton")
        layout.addWidget(import_button)

        return top_bar

    def _build_main_area(self) -> QWidget:
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_sidebar())
        splitter.addWidget(self._build_card_list())
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

        category_container = QWidget()
        category_layout = QVBoxLayout(category_container)
        category_layout.setContentsMargins(0, 0, 0, 0)
        category_layout.setSpacing(7)

        for name, count in CATEGORIES:
            category_layout.addWidget(self._build_category_row(name, count, name == "深度学习"))

        category_layout.addStretch(1)
        layout.addWidget(category_container, 1)

        divider = QFrame()
        divider.setObjectName("Divider")
        layout.addWidget(divider)

        draft_header = QHBoxLayout()
        draft_title = QLabel("草稿")
        draft_title.setObjectName("SectionTitle")
        draft_count = QLabel("5")
        draft_count.setObjectName("SectionCount")
        draft_count.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        draft_header.addWidget(draft_title)
        draft_header.addStretch(1)
        draft_header.addWidget(draft_count)
        layout.addLayout(draft_header)

        draft_input = QLineEdit()
        draft_input.setObjectName("DraftInput")
        draft_input.setPlaceholderText("快速记下一个标题...")
        layout.addWidget(draft_input)

        for draft in DRAFTS:
            layout.addWidget(self._build_draft_row(draft))

        return sidebar

    def _build_category_row(self, name: str, count: int, selected: bool = False) -> QWidget:
        row = QFrame()
        row.setObjectName("CategoryRow")
        row.setProperty("selected", "true" if selected else "false")

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

    def _build_draft_row(self, title: str) -> QWidget:
        row = QFrame()
        row.setObjectName("DraftRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(8, 0, 4, 0)
        layout.setSpacing(8)

        icon = QLabel("□")
        icon.setObjectName("DraftIcon")
        layout.addWidget(icon)

        label = QLabel(title)
        label.setObjectName("DraftTitle")
        label.setWordWrap(False)
        layout.addWidget(label, 1)

        return row

    def _build_card_list(self) -> QWidget:
        pane = QFrame()
        pane.setObjectName("ListPane")
        pane.setMinimumWidth(340)

        layout = QVBoxLayout(pane)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("知识卡片")
        title.setObjectName("SectionTitle")
        count = QLabel("共 4 条")
        count.setObjectName("SectionCount")
        header.addWidget(title)
        header.addSpacing(14)
        header.addWidget(count)
        header.addStretch(1)
        filter_icon = QLabel("筛选")
        filter_icon.setObjectName("MutedText")
        header.addWidget(filter_icon)
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_content = QWidget()
        card_layout = QVBoxLayout(scroll_content)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(14)

        for index, card in enumerate(CARDS):
            card_layout.addWidget(self._build_card_item(card, selected=index == 0))

        card_layout.addStretch(1)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)

        return pane

    def _build_card_item(self, card: dict[str, object], selected: bool = False) -> QWidget:
        item = QFrame()
        item.setObjectName("CardItem")
        item.setProperty("selected", "true" if selected else "false")

        layout = QVBoxLayout(item)
        layout.setContentsMargins(18, 16, 18, 14)
        layout.setSpacing(10)

        title = QLabel(str(card["title"]))
        title.setObjectName("CardTitle")
        title.setWordWrap(True)
        layout.addWidget(title)

        summary = QLabel(str(card["summary"]))
        summary.setObjectName("CardSummary")
        summary.setWordWrap(True)
        layout.addWidget(summary)

        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(8)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        for tag in card["tags"]:
            tag_label = QLabel(str(tag))
            tag_label.setObjectName("TagPill")
            tags_layout.addWidget(tag_label)
        tags_layout.addStretch(1)
        layout.addLayout(tags_layout)

        meta_layout = QHBoxLayout()
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(4)
        left_meta = QLabel(f"{card['category']} · {card['scenario']}")
        left_meta.setObjectName("CardMeta")
        right_meta = QLabel(f"更新于 {card['updated_at']}")
        right_meta.setObjectName("CardMeta")
        right_meta.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        meta_layout.addWidget(left_meta)
        meta_layout.addStretch(1)
        meta_layout.addWidget(right_meta)
        layout.addLayout(meta_layout)

        return item

    def _build_detail_pane(self) -> QWidget:
        pane = QFrame()
        pane.setObjectName("DetailPane")
        pane.setMinimumWidth(520)

        outer = QVBoxLayout(pane)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("DetailContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 44, 48, 40)
        layout.setSpacing(18)

        top = QHBoxLayout()
        title = QLabel(MLP_PREVIEW["title"])
        title.setObjectName("DetailTitle")
        title.setWordWrap(True)
        top.addWidget(title, 1)

        edit_button = QPushButton("编辑")
        edit_button.setObjectName("EditButton")
        top.addWidget(edit_button)

        delete_button = QPushButton("删除")
        delete_button.setObjectName("DeleteButton")
        top.addWidget(delete_button)
        layout.addLayout(top)

        layout.addSpacing(16)
        layout.addLayout(self._build_meta_row("用途场景：", MLP_PREVIEW["scenario"]))
        layout.addLayout(self._build_meta_row("分类：", MLP_PREVIEW["category"]))
        layout.addLayout(self._build_meta_row("标签：", MLP_PREVIEW["tags"], link_style=True))
        layout.addLayout(self._build_meta_row("一句话总结：", MLP_PREVIEW["summary"]))

        rule = QLabel()
        rule.setObjectName("HorizontalRule")
        layout.addSpacing(8)
        layout.addWidget(rule)
        layout.addSpacing(8)

        self._add_article_section(layout, "一、使用场景", "适用于图像分类、表格数据建模等结构化数据任务。")
        self._add_article_section(layout, "二、基本结构", "由若干全连接层（Linear）和激活函数（如 ReLU）堆叠组成。")

        heading = QLabel("三、PyTorch 最小代码")
        heading.setObjectName("ArticleHeading")
        layout.addWidget(heading)
        layout.addWidget(self._build_code_block())

        self._add_article_section(
            layout,
            "四、代码解释",
            "nn.Linear(784, 128)：输入维度为 784，输出维度为 128。\n"
            "nn.ReLU()：ReLU 激活函数，增加非线性能力。\n"
            "nn.Linear(128, 10)：输出维度为 10，适用于 10 类分类任务。",
        )
        self._add_article_section(
            layout,
            "五、注意事项",
            "根据任务调整层数和隐藏单元数。\n可搭配常见层如 Dropout、BatchNorm 等。",
        )

        layout.addStretch(1)
        scroll.setWidget(content)
        outer.addWidget(scroll)

        return pane

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

    def _add_article_section(self, layout: QVBoxLayout, heading_text: str, body_text: str) -> None:
        heading = QLabel(heading_text)
        heading.setObjectName("ArticleHeading")
        layout.addWidget(heading)

        for line in body_text.splitlines():
            text = QLabel(f"•  {line}")
            text.setObjectName("ArticleText")
            text.setWordWrap(True)
            layout.addWidget(text)

    def _build_code_block(self) -> QWidget:
        block = QFrame()
        block.setObjectName("CodeBlock")
        block.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(block)
        layout.setContentsMargins(16, 12, 16, 14)
        layout.setSpacing(7)

        lang = QLabel("python")
        lang.setObjectName("CodeLang")
        layout.addWidget(lang)

        for number, code in enumerate(MLP_PREVIEW["code"], start=1):
            line = QLabel(f"{number:<2}  {code}")
            line.setObjectName("CodeLine")
            line.setTextInteractionFlags(Qt.TextSelectableByMouse)
            layout.addWidget(line)

        return block

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
