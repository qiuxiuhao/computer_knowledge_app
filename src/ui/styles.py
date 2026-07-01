"""QSS styles for the Stage 1 static UI."""

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
QLineEdit#DraftInput {
    background: #FFFFFF;
    border: 1px solid #DDE3EC;
    border-radius: 9px;
    color: #111827;
    padding: 8px 12px;
    selection-background-color: #BFDBFE;
}

QLineEdit#SearchBox {
    min-height: 32px;
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

QPushButton#DeleteButton {
    background: #FFFFFF;
    border: 1px solid #DDE3EC;
    border-radius: 9px;
    color: #111827;
    font-weight: 600;
    padding: 9px 16px;
}

QFrame#Sidebar,
QFrame#ListPane {
    background: #F9FAFB;
    border-right: 1px solid #E5E7EB;
}

QFrame#DetailPane {
    background: #FFFFFF;
}

QWidget#DetailContent {
    background: #FFFFFF;
}

QLabel#SectionTitle {
    font-size: 16px;
    font-weight: 700;
}

QLabel#SectionCount,
QLabel#MutedText {
    color: #6B7280;
}

QFrame#CategoryRow {
    border-radius: 8px;
    min-height: 38px;
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
