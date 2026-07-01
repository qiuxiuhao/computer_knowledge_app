"""Data access functions for knowledge cards."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from src.db.database import DEFAULT_DB_PATH, get_connection, initialize_database
from src.models.card import Card

CARD_FIELDS = (
    "title",
    "scenario",
    "category",
    "tags",
    "summary",
    "content",
    "keywords",
    "source",
    "is_draft",
)

UPDATABLE_FIELDS = set(CARD_FIELDS)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _normalize_is_draft(value: int | bool) -> int:
    return 1 if bool(value) else 0


def create_card(
    *,
    title: str,
    scenario: str = "",
    category: str = "",
    tags: str = "",
    summary: str = "",
    content: str = "",
    keywords: str = "",
    source: str = "",
    is_draft: int | bool = 0,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> Card:
    """Create one formal or draft card and return the saved record."""
    if not title.strip():
        raise ValueError("title cannot be empty")

    initialize_database(db_path)
    timestamp = _now()

    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO cards (
                title, scenario, category, tags, summary, content,
                keywords, source, is_draft, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                title.strip(),
                scenario,
                category,
                tags,
                summary,
                content,
                keywords,
                source,
                _normalize_is_draft(is_draft),
                timestamp,
                timestamp,
            ),
        )
        connection.commit()
        card_id = int(cursor.lastrowid)

    card = get_card_by_id(card_id, db_path=db_path)
    if card is None:
        raise RuntimeError("created card could not be loaded")
    return card


def get_all_formal_cards(db_path: str | Path = DEFAULT_DB_PATH) -> list[Card]:
    """Return all formal cards, newest updated first."""
    return _get_cards_by_draft_state(0, db_path)


def get_all_draft_cards(db_path: str | Path = DEFAULT_DB_PATH) -> list[Card]:
    """Return all draft cards, newest updated first."""
    return _get_cards_by_draft_state(1, db_path)


def search_cards(
    keyword: str = "",
    *,
    category: str | None = None,
    db_path: str | Path = DEFAULT_DB_PATH,
) -> list[Card]:
    """Search formal cards with SQLite LIKE and optional category filtering."""
    initialize_database(db_path)

    normalized_keyword = keyword.strip()
    normalized_category = category.strip() if category else ""
    where_clauses = ["is_draft = 0"]
    parameters: list[str] = []

    if normalized_category and normalized_category != "全部":
        where_clauses.append("category = ?")
        parameters.append(normalized_category)

    like_value = f"%{normalized_keyword}%"
    if normalized_keyword:
        where_clauses.append(
            """
            (
                title LIKE ?
                OR summary LIKE ?
                OR tags LIKE ?
                OR keywords LIKE ?
                OR content LIKE ?
                OR category LIKE ?
                OR scenario LIKE ?
            )
            """
        )
        parameters.extend([like_value] * 7)

    where_sql = " AND ".join(where_clauses)

    if normalized_keyword:
        order_sql = """
        CASE
            WHEN title LIKE ? THEN 1
            WHEN tags LIKE ? THEN 2
            WHEN summary LIKE ? OR keywords LIKE ? THEN 3
            WHEN category LIKE ? OR scenario LIKE ? THEN 4
            WHEN content LIKE ? THEN 5
            ELSE 6
        END,
        updated_at DESC,
        id DESC
        """
        parameters.extend([like_value] * 7)
    else:
        order_sql = "updated_at DESC, id DESC"

    with get_connection(db_path) as connection:
        rows = connection.execute(
            f"""
            SELECT id, title, scenario, category, tags, summary, content,
                   keywords, source, is_draft, created_at, updated_at
            FROM cards
            WHERE {where_sql}
            ORDER BY {order_sql};
            """,
            parameters,
        ).fetchall()

    return [Card.from_row(row) for row in rows]


def get_card_by_id(card_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> Card | None:
    """Return one card by id, or None if it does not exist."""
    initialize_database(db_path)

    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT id, title, scenario, category, tags, summary, content,
                   keywords, source, is_draft, created_at, updated_at
            FROM cards
            WHERE id = ?;
            """,
            (card_id,),
        ).fetchone()

    return Card.from_row(row) if row else None


def update_card(
    card_id: int,
    *,
    db_path: str | Path = DEFAULT_DB_PATH,
    **fields: Any,
) -> Card | None:
    """Update allowed card fields and return the updated card."""
    if not fields:
        raise ValueError("no fields provided for update")

    unknown_fields = set(fields) - UPDATABLE_FIELDS
    if unknown_fields:
        names = ", ".join(sorted(unknown_fields))
        raise ValueError(f"unknown card field(s): {names}")

    if "title" in fields and not str(fields["title"]).strip():
        raise ValueError("title cannot be empty")

    initialize_database(db_path)

    cleaned_fields: dict[str, Any] = {}
    for key, value in fields.items():
        if key == "is_draft":
            cleaned_fields[key] = _normalize_is_draft(value)
        elif key == "title":
            cleaned_fields[key] = str(value).strip()
        else:
            cleaned_fields[key] = value

    cleaned_fields["updated_at"] = _now()
    assignments = ", ".join(f"{field} = ?" for field in cleaned_fields)
    values = list(cleaned_fields.values())
    values.append(card_id)

    with get_connection(db_path) as connection:
        cursor = connection.execute(
            f"UPDATE cards SET {assignments} WHERE id = ?;",
            values,
        )
        connection.commit()
        if cursor.rowcount == 0:
            return None

    return get_card_by_id(card_id, db_path=db_path)


def delete_card(card_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    """Delete one card by id. Return True if a row was deleted."""
    initialize_database(db_path)

    with get_connection(db_path) as connection:
        cursor = connection.execute("DELETE FROM cards WHERE id = ?;", (card_id,))
        connection.commit()
        return cursor.rowcount > 0


def save_draft_as_formal(card_id: int, db_path: str | Path = DEFAULT_DB_PATH) -> Card | None:
    """Convert a draft card into a formal card by setting is_draft to 0."""
    return update_card(card_id, db_path=db_path, is_draft=0)


def insert_sample_data(db_path: str | Path = DEFAULT_DB_PATH) -> list[Card]:
    """Insert sample cards for first-run and manual database-layer testing."""
    samples = [
        {
            "title": "MLP 是什么，以及 PyTorch 中一般怎么写",
            "scenario": "知识点",
            "category": "深度学习",
            "tags": "MLP, PyTorch, 神经网络, 全连接层",
            "summary": "MLP 是由多个全连接层和激活函数组成的神经网络结构。",
            "content": (
                "一、使用场景\n"
                "- 适用于图像分类、表格数据建模等结构化数据任务。\n\n"
                "二、基本结构\n"
                "- 由若干全连接层（Linear）和激活函数（如 ReLU）堆叠组成。\n\n"
                "三、PyTorch 最小代码\n\n"
                "```python\n"
                "import torch.nn as nn\n\n"
                "model = nn.Sequential(\n"
                "    nn.Linear(784, 128),\n"
                "    nn.ReLU(),\n"
                "    nn.Linear(128, 10)\n"
                ")\n"
                "```\n\n"
                "四、注意事项\n"
                "- 根据任务调整层数和隐藏单元数。"
            ),
            "keywords": "MLP, Linear, ReLU",
            "source": "",
            "is_draft": 0,
        },
        {
            "title": "Mac 终端提示 zsh: command not found: conda 怎么解决",
            "scenario": "问题解决",
            "category": "报错解决",
            "tags": "zsh, conda, Mac, 终端",
            "summary": "分析 conda 命令无法找到的常见原因，并记录排查和修复方法。",
            "content": (
                "一、常见原因\n"
                "- conda 没有安装。\n"
                "- shell 初始化脚本没有写入 PATH。\n"
                "- 终端没有重新加载配置。\n\n"
                "二、可先检查\n\n"
                "```bash\n"
                "which conda\n"
                "echo $PATH\n"
                "```\n\n"
                "三、处理思路\n"
                "- 确认 Miniforge 或 Anaconda 安装路径。\n"
                "- 重新初始化 shell 或手动补充 PATH。"
            ),
            "keywords": "zsh, conda, PATH",
            "source": "",
            "is_draft": 0,
        },
        {
            "title": "tmux 常用命令整理",
            "scenario": "常用命令",
            "category": "常用命令",
            "tags": "tmux, 终端, 效率工具",
            "summary": "整理 tmux 常用会话、窗口和后台运行命令。",
            "content": (
                "一、创建会话\n\n"
                "```bash\n"
                "tmux new -s train\n"
                "```\n\n"
                "二、恢复会话\n\n"
                "```bash\n"
                "tmux attach -t train\n"
                "```\n\n"
                "三、查看会话\n\n"
                "```bash\n"
                "tmux ls\n"
                "```"
            ),
            "keywords": "tmux, session, terminal",
            "source": "",
            "is_draft": 0,
        },
        {
            "title": "AutoDL 上创建 conda 环境的完整流程",
            "scenario": "实践教程",
            "category": "AutoDL",
            "tags": "AutoDL, conda, 环境配置",
            "summary": "记录在 AutoDL 上从创建环境到安装依赖的基础流程。",
            "content": (
                "一、创建环境\n\n"
                "```bash\n"
                "conda create -n myenv python=3.11\n"
                "conda activate myenv\n"
                "```\n\n"
                "二、安装依赖\n"
                "- 优先根据项目 README 安装。\n"
                "- 注意 CUDA 和 PyTorch 版本匹配。"
            ),
            "keywords": "AutoDL, conda, PyTorch",
            "source": "",
            "is_draft": 0,
        },
        {
            "title": "什么是 CUDA OOM",
            "scenario": "",
            "category": "",
            "tags": "",
            "summary": "",
            "content": "",
            "keywords": "CUDA OOM, 显存不足",
            "source": "",
            "is_draft": 1,
        },
        {
            "title": "conda 和 pip 的区别",
            "scenario": "",
            "category": "",
            "tags": "",
            "summary": "",
            "content": "",
            "keywords": "conda, pip",
            "source": "",
            "is_draft": 1,
        },
        {
            "title": "tmux 为什么能后台运行",
            "scenario": "",
            "category": "",
            "tags": "",
            "summary": "",
            "content": "",
            "keywords": "tmux, 后台运行",
            "source": "",
            "is_draft": 1,
        },
        {
            "title": "macOS 里的 PATH 是什么",
            "scenario": "",
            "category": "",
            "tags": "",
            "summary": "",
            "content": "",
            "keywords": "macOS, PATH",
            "source": "",
            "is_draft": 1,
        },
    ]

    return [create_card(db_path=db_path, **sample) for sample in samples]


def ensure_sample_data_if_empty(db_path: str | Path = DEFAULT_DB_PATH) -> bool:
    """Insert sample data only when the cards table is completely empty."""
    initialize_database(db_path)

    with get_connection(db_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM cards;").fetchone()[0]

    if count > 0:
        return False

    insert_sample_data(db_path)
    return True


def _get_cards_by_draft_state(is_draft: int, db_path: str | Path) -> list[Card]:
    initialize_database(db_path)

    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT id, title, scenario, category, tags, summary, content,
                   keywords, source, is_draft, created_at, updated_at
            FROM cards
            WHERE is_draft = ?
            ORDER BY updated_at DESC, id DESC;
            """,
            (is_draft,),
        ).fetchall()

    return [Card.from_row(row) for row in rows]
