"""Conservative Markdown normalization and repair helpers."""

from __future__ import annotations

import re


def normalize_markdown(content: str) -> str:
    """Normalize Markdown without rewriting fenced code block contents."""
    text = content.replace("\r\n", "\n").replace("\r", "\n")
    if not text.strip():
        return ""

    segments = _split_fenced_code_blocks(text)
    normalized_parts: list[str] = []
    for kind, segment in segments:
        if kind == "code":
            normalized_parts.append(_normalize_code_block(segment))
        else:
            normalized_parts.append(_normalize_markdown_text(segment))

    normalized = "\n\n".join(part for part in normalized_parts if part)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.rstrip() + "\n"


def best_effort_repair_markdown(content: str) -> str:
    """Try to repair obvious one-line Markdown damage without overwriting data."""
    text = content.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+(#{1,6}\s+)", r"\n\n\1", text)
    text = re.sub(r"[ \t]+(```[A-Za-z0-9_-]*)[ \t]+", r"\n\n\1\n", text)
    text = re.sub(r"[ \t]+```[ \t]+", "\n```\n\n", text)
    text = re.sub(r"(```[A-Za-z0-9_-]*)[ \t]+", r"\1\n", text)
    text = re.sub(r"[ \t]+```", "\n```", text)
    return normalize_markdown(text)


def _split_fenced_code_blocks(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines(keepends=True)
    segments: list[tuple[str, str]] = []
    prose_lines: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        start_match = re.match(r"^[ \t]*(`{3,})([^`]*)\n?$", line)
        if start_match is None:
            prose_lines.append(line)
            index += 1
            continue

        if prose_lines:
            segments.append(("text", "".join(prose_lines)))
            prose_lines = []

        fence = start_match.group(1)
        code_lines = [line]
        index += 1
        closing_pattern = rf"^[ \t]*{re.escape(fence)}[ \t]*\n?$"
        while index < len(lines):
            code_lines.append(lines[index])
            if re.match(closing_pattern, lines[index]):
                index += 1
                break
            index += 1
        segments.append(("code", "".join(code_lines)))

    if prose_lines:
        segments.append(("text", "".join(prose_lines)))

    return segments


def _normalize_markdown_text(text: str) -> str:
    lines = [line.rstrip() for line in text.split("\n")]
    output: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if output and output[-1] != "":
                output.append("")
            continue

        if re.match(r"^#{1,6}\s+", stripped):
            if output and output[-1] != "":
                output.append("")
            output.append(stripped)
            output.append("")
            continue

        output.append(line.rstrip())

    while output and output[-1] == "":
        output.pop()
    while output and output[0] == "":
        output.pop(0)

    return "\n".join(output)


def _normalize_code_block(block: str) -> str:
    block = block.strip("\n")
    return block

