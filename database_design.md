# Database Design

本文档记录第一版数据库设计。当前阶段只做设计说明，不创建 SQLite 数据库文件，不初始化数据库，不写数据库业务代码。

## 1. 设计原则

第一版数据库保持简单稳定，以 `cards` 表为核心。

草稿也是知识卡片，通过 `is_draft` 字段区分：

```text
is_draft = 1：草稿卡片
is_draft = 0：正式知识卡片
```

第一版不设计：

- `todos` 表
- `to_complete` 表
- `favorites` 表
- 独立草稿表
- 复杂任务状态表

## 2. 核心表：cards

计划表名：

```text
cards
```

计划字段：

| 字段 | 类型建议 | 说明 |
|---|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | 唯一卡片 ID |
| `title` | TEXT NOT NULL | 卡片标题 |
| `scenario` | TEXT | 使用场景 |
| `category` | TEXT | 分类 |
| `tags` | TEXT | 标签，第一版可用逗号分隔文本 |
| `summary` | TEXT | 一句话总结 |
| `content` | TEXT | Markdown 原文内容 |
| `keywords` | TEXT | 额外搜索关键词 |
| `source` | TEXT | 来源链接或来源说明 |
| `is_draft` | INTEGER NOT NULL DEFAULT 0 | 是否为草稿，1 表示草稿，0 表示正式卡片 |
| `created_at` | TEXT NOT NULL | 创建时间 |
| `updated_at` | TEXT NOT NULL | 更新时间 |

## 3. 草稿存储方式

草稿不单独建表。

当用户在左侧底部草稿区快速输入标题时，后续实现中应创建一条 `cards` 记录：

```text
title = 用户输入的标题
is_draft = 1
```

其他字段可以暂时为空，等用户点击草稿并继续编辑时再补充。

草稿保存为正式卡片时：

```text
is_draft = 0
```

该卡片从左侧草稿区移除，显示到中间正式知识卡片列表中。

## 4. 正式卡片查询规则

中间知识卡片列表默认只显示：

```sql
WHERE is_draft = 0
```

左侧草稿区只显示：

```sql
WHERE is_draft = 1
```

## 5. 搜索设计

第一版后续可使用 SQLite `LIKE` 做普通关键词搜索。

搜索范围：

- `title`
- `summary`
- `tags`
- `keywords`
- `content`
- `category`
- `scenario`

搜索结果默认只面向正式卡片：

```sql
WHERE is_draft = 0
```

当前 Stage 0 不实现真实搜索。

## 6. 后续可能扩展

后续版本在确有需要时，可以考虑：

- `tags` 表
- `categories` 表
- `attachments` 表
- SQLite FTS 全文搜索表
- 数据库迁移机制

在修改数据库结构前，应先说明修改原因和影响，不能直接删除字段或覆盖用户真实数据。

