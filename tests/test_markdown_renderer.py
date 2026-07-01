"""Tests for Markdown preview rendering."""

from __future__ import annotations

import unittest

from src.utils.markdown_renderer import render_markdown_to_html


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


if __name__ == "__main__":
    unittest.main()

