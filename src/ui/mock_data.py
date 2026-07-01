"""Static mock data for the Stage 1 UI."""

from __future__ import annotations

CATEGORIES = [
    ("全部", 119),
    ("Python", 22),
    ("深度学习", 18),
    ("PyTorch", 14),
    ("AutoDL", 9),
    ("Mac", 16),
    ("Linux", 15),
    ("Conda", 11),
    ("Git", 12),
    ("常用命令", 20),
    ("报错解决", 21),
    ("项目经验", 13),
    ("论文笔记", 8),
]

DRAFTS = [
    "什么是 CUDA OOM",
    "conda 和 pip 的区别",
    "tmux 为什么能后台运行",
    "macOS 里的 PATH 是什么",
]

CARDS = [
    {
        "title": "MLP 是什么，以及 PyTorch 中一般怎么写",
        "summary": "介绍 MLP 的定义、结构和在 PyTorch 中的最小实现方式。",
        "tags": ["MLP", "PyTorch", "神经网络", "全连接层"],
        "category": "深度学习",
        "scenario": "知识点",
        "updated_at": "2024-05-12 10:30",
    },
    {
        "title": "Mac 终端提示 zsh: command not found: conda 怎么解决",
        "summary": "分析原因并提供多种有效的解决方案，适用于不同安装方式。",
        "tags": ["zsh", "conda", "Mac", "终端"],
        "category": "报错解决",
        "scenario": "问题解决",
        "updated_at": "2024-05-10 16:45",
    },
    {
        "title": "tmux 常用命令整理",
        "summary": "整理 tmux 常用命令、快捷键和使用技巧，提高终端效率。",
        "tags": ["tmux", "终端", "效率工具"],
        "category": "常用命令",
        "scenario": "常用命令",
        "updated_at": "2024-05-08 09:18",
    },
    {
        "title": "AutoDL 上创建 conda 环境的完整流程",
        "summary": "从创建环境到安装依赖的完整步骤，附常见问题处理。",
        "tags": ["AutoDL", "conda", "环境配置"],
        "category": "AutoDL",
        "scenario": "实践教程",
        "updated_at": "2024-05-05 14:22",
    },
]

MLP_PREVIEW = {
    "title": "MLP 是什么，以及 PyTorch 中一般怎么写",
    "scenario": "知识点",
    "category": "深度学习",
    "tags": "MLP / PyTorch / 神经网络 / 全连接层",
    "summary": "MLP 是由多个全连接层和激活函数组成的神经网络结构。",
    "code": [
        "import torch.nn as nn",
        "",
        "model = nn.Sequential(",
        "    nn.Linear(784, 128),",
        "    nn.ReLU(),",
        "    nn.Linear(128, 10)",
        ")",
    ],
}

