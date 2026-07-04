"""QSS styles for the PySide6 desktop UI."""

APP_STYLE = """
QMainWindow {
    background: #F8FAFC;
}

QWidget {
    color: #111827;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial;
    font-size: 14px;
}

QFrame#TopBar {
    background: #FFFFFF;
    border-bottom: 1px solid #E5E7EB;
}

QLabel#AppName {
    font-size: 17px;
    font-weight: 700;
}

QLabel#CurrentPage {
    color: #2563EB;
    font-size: 15px;
    font-weight: 700;
    border-bottom: 3px solid #2563EB;
    padding: 18px 20px 17px 20px;
}

QLineEdit#SearchBox,
QLineEdit#DraftInput,
QLineEdit#EditorInput,
QComboBox#EditorInput {
    background: #FFFFFF;
    border: 1px solid #DDE3EC;
    border-radius: 9px;
    color: #111827;
    padding: 8px 12px;
    selection-background-color: #BFDBFE;
}

QComboBox#EditorInput {
    padding-right: 44px;
}

QLineEdit#SearchBox {
    min-height: 32px;
}

QTextEdit#EditorTextArea,
QTextEdit#PreviewBody,
QTextBrowser#PreviewBody {
    background: #FFFFFF;
    border: 1px solid #DDE3EC;
    border-radius: 9px;
    color: #111827;
    font-size: 14px;
    line-height: 1.6;
    padding: 10px;
    selection-background-color: #BFDBFE;
}

QTextEdit#PreviewBody,
QTextBrowser#PreviewBody {
    background: #F8FAFC;
    font-family: "SF Pro Text", "Helvetica Neue", Arial;
}

QTextBrowser#MarkdownTextBlock {
    background: transparent;
    border: none;
    color: #111827;
    padding: 0;
}

QComboBox#EditorInput::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    background: #EFF6FF;
    border-left: 1px solid #DDE3EC;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
    width: 38px;
}

QComboBox#EditorInput::drop-down:hover {
    background: #DBEAFE;
}

QPushButton#PrimaryButton {
    background: #2563EB;
    border: 1px solid #2563EB;
    border-radius: 9px;
    color: #FFFFFF;
    font-weight: 700;
    padding: 9px 18px;
}

QPushButton#SecondaryButton,
QPushButton#EditButton {
    background: #FFFFFF;
    border: 1px solid #DDE3EC;
    border-radius: 9px;
    color: #111827;
    font-weight: 600;
    padding: 9px 16px;
}

QPushButton#CodeCopyButton {
    background: #FFFFFF;
    border: 1px solid #DDE3EC;
    border-radius: 7px;
    color: #2563EB;
    font-size: 12px;
    font-weight: 700;
    padding: 5px 10px;
}

QPushButton#CodeCopyButton:hover {
    background: #EFF6FF;
}

QPushButton#DeleteButton {
    background: #FFFFFF;
    border: 1px solid #DDE3EC;
    border-radius: 9px;
    color: #111827;
    font-weight: 600;
    padding: 9px 16px;
}

QPushButton#DraftAddButton {
    background: #2563EB;
    border: 1px solid #2563EB;
    border-radius: 8px;
    color: #FFFFFF;
    font-weight: 700;
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
}

QPushButton#DraftDeleteButton {
    background: transparent;
    border: none;
    color: #DC2626;
    font-size: 12px;
    padding: 2px 4px;
}

QFrame#Sidebar,
QFrame#ListPane,
QFrame#UnifiedSidebar {
    background: #F9FAFB;
    border-right: 1px solid #E5E7EB;
}

QFrame#DetailPane {
    background: #FFFFFF;
}

QFrame#DetailToolbar {
    background: #FFFFFF;
    border-bottom: 1px solid #E5E7EB;
    min-height: 64px;
    max-height: 64px;
}

QWidget#DetailContent {
    background: #FFFFFF;
}

QDialog#FullScreenReader {
    background: #FFFFFF;
}

QFrame#FullScreenToolbar {
    background: #FFFFFF;
    border-bottom: 1px solid #E5E7EB;
    min-height: 68px;
    max-height: 68px;
}

QFrame#FullScreenContent {
    background: #FFFFFF;
}

QLabel#FullScreenTitle {
    font-size: 19px;
    font-weight: 800;
}

QLabel#CopyStatus {
    color: #2563EB;
    font-size: 13px;
    font-weight: 700;
    min-width: 80px;
}

QLabel#SectionTitle {
    font-size: 16px;
    font-weight: 700;
}

QLabel#SectionCount,
QLabel#MutedText {
    color: #6B7280;
}

QFrame#CollapseHeader {
    border-radius: 8px;
    min-height: 36px;
}

QFrame#CollapseHeader:hover {
    background: #EFF6FF;
}

QScrollArea#CategoryScroll {
    max-height: 286px;
}

QLabel#CollapseArrow {
    min-width: 22px;
    max-width: 22px;
    min-height: 22px;
    max-height: 22px;
}

QLabel#DetailModeLabel {
    color: #374151;
    font-size: 15px;
    font-weight: 700;
}

QFrame#CategoryRow {
    border-radius: 8px;
    min-height: 38px;
    max-height: 38px;
}

QFrame#CategoryRow[selected="true"] {
    background: #EFF6FF;
}

QLabel#CategoryName {
    font-size: 14px;
}

QFrame#CategoryRow[selected="true"] QLabel#CategoryName,
QFrame#CategoryRow[selected="true"] QLabel#CategoryCount {
    color: #2563EB;
    font-weight: 700;
}

QLabel#CategoryIcon {
    color: #2563EB;
    font-weight: 700;
    min-width: 20px;
}

QLabel#CategoryCount {
    color: #4B5563;
}

QFrame#Divider {
    background: #E5E7EB;
    min-height: 1px;
    max-height: 1px;
}

QFrame#DraftRow {
    border-radius: 7px;
    min-height: 28px;
}

QFrame#DraftRow:hover {
    background: #EFF6FF;
}

QLabel#DraftIcon,
QLabel#DraftTitle {
    color: #374151;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #CBD5E1;
    border-radius: 4px;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QFrame#CardItem {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
}

QFrame#CardItem[selected="true"] {
    background: #FFFFFF;
    border: 2px solid #2563EB;
}

QLabel#CardTitle {
    font-size: 15px;
    font-weight: 700;
    line-height: 1.3;
}

QLabel#CardSummary {
    color: #374151;
    font-size: 13px;
    line-height: 1.4;
}

QLabel#TagPill {
    background: #EFF6FF;
    border-radius: 6px;
    color: #2563EB;
    font-size: 12px;
    font-weight: 700;
    padding: 4px 8px;
}

QLabel#CardMeta {
    color: #6B7280;
    font-size: 12px;
}

QLabel#DetailTitle {
    font-size: 24px;
    font-weight: 800;
}

QLabel#MetaLabel {
    color: #374151;
    min-width: 90px;
}

QLabel#MetaValue {
    color: #111827;
}

QLabel#MetaValueLink {
    color: #2563EB;
    font-weight: 600;
}

QLabel#HorizontalRule {
    background: #E5E7EB;
    min-height: 1px;
    max-height: 1px;
}

QLabel#ArticleHeading {
    font-size: 17px;
    font-weight: 800;
    margin-top: 8px;
}

QLabel#ArticleText {
    color: #111827;
    line-height: 1.6;
}

QWidget#MarkdownReader {
    background: transparent;
}

QFrame#CopyableCodeBlock {
    background: #F8FAFC;
    border: 1px solid #DDE3EC;
    border-radius: 8px;
}

QFrame#CodeBlockHeader {
    background: #F1F5F9;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    min-height: 42px;
    max-height: 42px;
}

QLabel#CodeBlockLanguage {
    color: #64748B;
    font-family: "SF Mono", Menlo, Monaco, Consolas, monospace;
    font-size: 12px;
    font-weight: 700;
}

QPlainTextEdit#CodeBlockText {
    background: #F8FAFC;
    border: none;
    color: #111827;
    font-family: "SF Mono", Menlo, Monaco, Consolas, monospace;
    font-size: 13px;
    line-height: 1.55;
    padding: 12px 14px;
    selection-background-color: #BFDBFE;
}

QFrame#CodeBlock {
    background: #F8FAFC;
    border: 1px solid #DDE3EC;
    border-radius: 8px;
}

QLabel#CodeLang {
    color: #6B7280;
    font-family: "SF Mono", Menlo, Monaco, Consolas, monospace;
    font-size: 12px;
}

QLabel#CodeLine {
    color: #111827;
    font-family: "SF Mono", Menlo, Monaco, Consolas, monospace;
    font-size: 13px;
}
"""
