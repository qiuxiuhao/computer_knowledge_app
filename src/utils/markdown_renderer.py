"""Markdown to HTML rendering helpers for the local preview pane."""

from __future__ import annotations

import html

import markdown

MARKDOWN_CSS = """
body {
    color: #111827;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
    font-size: 14px;
    line-height: 1.7;
}

h1, h2, h3, h4 {
    color: #111827;
    font-weight: 800;
    margin: 18px 0 10px 0;
}

h1 { font-size: 24px; }
h2 { font-size: 20px; }
h3 { font-size: 17px; }
h4 { font-size: 15px; }

p {
    margin: 8px 0 12px 0;
}

ul, ol {
    margin: 8px 0 14px 24px;
    padding: 0;
}

li {
    margin: 4px 0;
}

code {
    background: #EEF2FF;
    border-radius: 4px;
    color: #1D4ED8;
    font-family: "SF Mono", Menlo, Monaco, Consolas, monospace;
    font-size: 13px;
    padding: 2px 5px;
}

pre {
    background: #F8FAFC;
    border: 1px solid #DDE3EC;
    border-radius: 8px;
    color: #111827;
    font-family: "SF Mono", Menlo, Monaco, Consolas, monospace;
    font-size: 13px;
    line-height: 1.55;
    margin: 12px 0 18px 0;
    padding: 12px 14px;
    white-space: pre-wrap;
}

pre code {
    background: transparent;
    color: #111827;
    padding: 0;
}

blockquote {
    border-left: 4px solid #BFDBFE;
    color: #374151;
    margin: 12px 0;
    padding: 4px 0 4px 14px;
}

table {
    border-collapse: collapse;
    margin: 12px 0 18px 0;
    width: 100%;
}

th, td {
    border: 1px solid #DDE3EC;
    padding: 7px 9px;
}

th {
    background: #EFF6FF;
    font-weight: 700;
}

a {
    color: #2563EB;
    text-decoration: none;
}
"""


def render_markdown_to_html(markdown_text: str) -> str:
    """Render Markdown text to a full HTML document for QTextBrowser."""
    source = markdown_text.strip() or "暂无正文内容。"
    try:
        body = markdown.markdown(
            source,
            extensions=["extra", "sane_lists"],
            output_format="html5",
        )
    except Exception:
        body = f"<pre>{html.escape(source)}</pre>"

    return f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>{MARKDOWN_CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""

