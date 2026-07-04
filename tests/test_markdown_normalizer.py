"""Tests for conservative Markdown normalization."""

from __future__ import annotations

import unittest

from src.utils.markdown_normalizer import best_effort_repair_markdown, normalize_markdown
from src.utils.markdown_renderer import parse_markdown_segments, render_markdown_to_html


ROUNDTRIP_MARKDOWN = """## 环境配置

中文段落包含 `conda activate` 行内代码。

```bash
# 进入环境
conda activate computer_knowledge_app
python -m src.main --smoke-test
```

保存后代码块不能被压成一行。
"""


class MarkdownNormalizerTest(unittest.TestCase):
    def test_normalize_preserves_fenced_code_block(self) -> None:
        normalized = normalize_markdown(ROUNDTRIP_MARKDOWN.replace("\n", "\r\n"))

        self.assertIn("## 环境配置\n\n", normalized)
        self.assertIn("中文段落包含 `conda activate` 行内代码。", normalized)
        self.assertIn("```bash\n# 进入环境\nconda activate computer_knowledge_app\n", normalized)
        self.assertIn("python -m src.main --smoke-test\n```", normalized)
        self.assertTrue(normalized.endswith("\n"))

        segments = parse_markdown_segments(normalized)
        code_segments = [segment for segment in segments if segment.kind == "code"]
        self.assertEqual(len(code_segments), 1)
        self.assertEqual(code_segments[0].language, "bash")
        self.assertIn("# 进入环境", code_segments[0].text)
        self.assertIn("\npython -m src.main --smoke-test", code_segments[0].text)

    def test_render_after_normalize_still_recognizes_code_block(self) -> None:
        html = render_markdown_to_html(normalize_markdown(ROUNDTRIP_MARKDOWN))

        self.assertIn("<h2>", html)
        self.assertIn("<code>", html)
        self.assertIn("<pre>", html)

    def test_best_effort_repair_obvious_one_line_damage(self) -> None:
        damaged = "说明 ### 标题 ```bash echo hello ``` 结束"
        repaired = best_effort_repair_markdown(damaged)

        self.assertIn("\n\n### 标题", repaired)
        self.assertIn("```bash\n", repaired)


if __name__ == "__main__":
    unittest.main()

