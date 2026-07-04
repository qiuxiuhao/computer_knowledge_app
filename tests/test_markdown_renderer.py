"""Tests for Markdown preview rendering."""

from __future__ import annotations

import unittest

from src.utils.markdown_renderer import parse_markdown_segments, render_markdown_to_html


class MarkdownRendererTest(unittest.TestCase):
    def test_render_common_markdown_features(self) -> None:
        html = render_markdown_to_html(
            """# 标题

段落包含 `inline code`。

1. 第一项
2. 第二项

- 无序项

> 引用内容

| 字段 | 含义 |
|---|---|
| title | 标题 |

```python
print("hello")
```
"""
        )

        self.assertIn("<h1>", html)
        self.assertIn("<code>", html)
        self.assertIn("<ol>", html)
        self.assertIn("<ul>", html)
        self.assertIn("<blockquote>", html)
        self.assertIn("<table>", html)
        self.assertIn("<pre>", html)
        self.assertIn("line-height: 1.82", html)
        self.assertIn("border-left: 4px solid #BFDBFE", html)

    def test_parse_fenced_code_blocks_preserves_language_and_code(self) -> None:
        segments = parse_markdown_segments(
            """# 命令记录

先执行 bash 命令：

```bash
conda activate computer_knowledge_app
python -m src.main
```

再看 Python：

```python
print("hello")
```
"""
        )

        self.assertEqual([segment.kind for segment in segments], ["markdown", "code", "markdown", "code"])
        self.assertEqual(segments[1].language, "bash")
        self.assertEqual(
            segments[1].text,
            "conda activate computer_knowledge_app\npython -m src.main",
        )
        self.assertEqual(segments[3].language, "python")
        self.assertEqual(segments[3].text, 'print("hello")')


if __name__ == "__main__":
    unittest.main()
