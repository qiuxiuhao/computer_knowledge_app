"""Markdown block parsing and serialization for the editor UI."""

from __future__ import annotations

from dataclasses import dataclass
import re


DEFAULT_CODE_LANGUAGES = [
    "text",
    "bash",
    "python",
    "json",
    "markdown",
    "yaml",
    "sql",
]


@dataclass(frozen=True)
class MarkdownBlock:
    """One editable Markdown body block."""

    kind: str
    text: str
    language: str = ""


class MarkdownBlockParseError(ValueError):
    """Raised when Markdown cannot be safely represented as editor blocks."""


def parse_markdown_blocks(markdown_text: str) -> list[MarkdownBlock]:
    """Parse Markdown into text and fenced-code blocks.

    The parser is intentionally conservative. If a fenced code block is opened
    but not closed, callers should keep the original Markdown source instead of
    trying to repair it in the block editor.
    """
    if not markdown_text:
        return [MarkdownBlock(kind="text", text="")]

    text = markdown_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.splitlines(keepends=True)
    blocks: list[MarkdownBlock] = []
    prose_lines: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        start_match = re.match(r"^[ \t]*(`{3,})([^`]*)\n?$", line)
        if start_match is None:
            prose_lines.append(line)
            index += 1
            continue

        _append_text_block(blocks, prose_lines)
        prose_lines = []

        fence = start_match.group(1)
        language = start_match.group(2).strip().split(" ", 1)[0] or "text"
        closing_pattern = rf"^[ \t]*{re.escape(fence)}[ \t]*\n?$"
        index += 1
        code_lines: list[str] = []
        closed = False

        while index < len(lines):
            if re.match(closing_pattern, lines[index]):
                closed = True
                index += 1
                break
            code_lines.append(lines[index])
            index += 1

        if not closed:
            raise MarkdownBlockParseError("unclosed fenced code block")

        blocks.append(
            MarkdownBlock(
                kind="code",
                text=_strip_single_trailing_newline("".join(code_lines)),
                language=language,
            )
        )

    _append_text_block(blocks, prose_lines)
    return blocks or [MarkdownBlock(kind="text", text="")]


def serialize_markdown_blocks(blocks: list[MarkdownBlock]) -> str:
    """Serialize editor blocks into standard Markdown."""
    parts: list[str] = []

    for block in blocks:
        text = block.text.rstrip()
        if not text:
            continue

        if block.kind == "code":
            language = (block.language or "text").strip() or "text"
            fence = _choose_fence(text)
            parts.append(f"{fence}{language}\n{text}\n{fence}")
        else:
            parts.append(text)

    return "\n\n".join(parts)


def collect_code_languages(blocks: list[MarkdownBlock]) -> list[str]:
    """Return default languages plus custom languages found in parsed blocks."""
    languages = list(DEFAULT_CODE_LANGUAGES)
    seen = set(languages)
    for block in blocks:
        language = block.language.strip()
        if block.kind != "code" or not language or language in seen:
            continue
        languages.append(language)
        seen.add(language)
    return languages


def _append_text_block(blocks: list[MarkdownBlock], lines: list[str]) -> None:
    text = "".join(lines).strip("\n")
    if text:
        blocks.append(MarkdownBlock(kind="text", text=text))


def _strip_single_trailing_newline(text: str) -> str:
    if text.endswith("\n"):
        return text[:-1]
    return text


def _choose_fence(code: str) -> str:
    longest_run = max((len(match.group(0)) for match in re.finditer(r"`+", code)), default=0)
    return "`" * max(3, longest_run + 1)
