"""Markdown to HTML rendering helpers for the local preview pane."""

from __future__ import annotations

from dataclasses import dataclass
import html
import re

import markdown

MARKDOWN_CSS = """
body {
    color: #111827;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
    font-size: 16px;
    line-height: 1.82;
    margin: 0;
    padding: 0;
}

h1, h2, h3, h4 {
    color: #111827;
    font-weight: 800;
    line-height: 1.28;
    margin: 26px 0 14px 0;
}

h1 {
    border-bottom: 1px solid #E5E7EB;
    font-size: 28px;
    padding-bottom: 10px;
}

h2 { font-size: 23px; }
h3 { font-size: 19px; }
h4 { font-size: 16px; }

p {
    margin: 0 0 18px 0;
}

ul, ol {
    margin: 8px 0 20px 28px;
    padding: 0;
}

li {
    margin: 7px 0;
}

code {
    background: #F1F5F9;
    border-radius: 4px;
    color: #1E40AF;
    font-family: "SF Mono", Menlo, Monaco, Consolas, monospace;
    font-size: 14px;
    padding: 2px 6px;
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
    background: #F8FAFC;
    color: #374151;
    margin: 16px 0 22px 0;
    padding: 12px 16px;
}

table {
    border-collapse: collapse;
    margin: 16px 0 24px 0;
    width: 100%;
}

th, td {
    border: 1px solid #DDE3EC;
    padding: 9px 11px;
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


@dataclass(frozen=True)
class MarkdownSegment:
    """One markdown prose or fenced code segment."""

    kind: str
    text: str
    language: str = ""


def parse_markdown_segments(markdown_text: str) -> list[MarkdownSegment]:
    """Split Markdown into prose and fenced code blocks."""
    lines = markdown_text.splitlines(keepends=True)
    segments: list[MarkdownSegment] = []
    prose_lines: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        start_match = re.match(r"^[ \t]*(`{3,})([^`]*)\r?\n?$", line)
        if start_match is None:
            prose_lines.append(line)
            index += 1
            continue

        if prose_lines:
            prose = "".join(prose_lines).strip()
            if prose:
                segments.append(MarkdownSegment(kind="markdown", text=prose))
            prose_lines = []

        fence = start_match.group(1)
        language = start_match.group(2).strip().split(" ", 1)[0]
        index += 1
        code_lines: list[str] = []
        closing_pattern = rf"^[ \t]*{re.escape(fence)}[ \t]*\r?\n?$"

        while index < len(lines):
            if re.match(closing_pattern, lines[index]):
                index += 1
                break
            code_lines.append(lines[index])
            index += 1

        code = "".join(code_lines)
        if code.endswith("\n"):
            code = code[:-1]
        if code.endswith("\r"):
            code = code[:-1]
        segments.append(MarkdownSegment(kind="code", text=code, language=language))

    if prose_lines:
        prose = "".join(prose_lines).strip()
        if prose:
            segments.append(MarkdownSegment(kind="markdown", text=prose))

    if not segments:
        segments.append(MarkdownSegment(kind="markdown", text=""))

    return segments


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
