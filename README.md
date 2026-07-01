# Personal Computer Knowledge Base

本项目是一个本地 macOS 桌面应用，用来记录、整理、搜索和回看个人计算机学习过程中的知识卡片。

项目第一版的目标是简单、稳定、本地可用，优先服务于初学者记录学习笔记、报错解决、常用命令、项目经验和论文笔记。

## 项目定位

- 这是一个本地桌面应用，不是 Web 应用。
- 这是一个个人知识库，不是 AI 聊天工具。
- 数据计划保存在本地 SQLite 数据库中。
- 知识卡片正文计划使用 Markdown 原文保存。
- 第一版只保留一个页面：知识库主页面。

## 第一版页面范围

第一版只设计并逐步实现：

```text
Knowledge Base Main Page
知识库主页面
```

页面结构为三列：

```text
左侧：分类 + 底部草稿
中间：知识卡片列表
右侧：卡片预览 / 编辑区
```

顶部区域包含：

- 应用名称：Personal Computer Knowledge Base / 个人计算机知识库
- 当前页面：Knowledge Base / 知识库
- 搜索框
- 新建卡片按钮
- 导入按钮
- 用户 / 设置入口

## 第一版不包含

第一版不做以下内容：

- 独立待补充页面
- 收藏功能
- 常用标签侧栏
- 复杂任务管理系统
- AI 问答
- 云同步
- 登录系统
- Web 版本
- 语义搜索或向量数据库

## 草稿设计

草稿不属于任务系统，也不是待办事项。

草稿本质上是一张未完成的知识卡片：

```text
is_draft = 1
```

草稿放在左侧栏底部。用户可以快速写下一个标题，之后点击草稿标题，在右侧直接进入编辑模式继续补充。

当草稿保存为正式知识卡片后：

```text
is_draft = 0
```

它会从左侧草稿区消失，进入中间的正式知识卡片列表。

## 推荐分类

第一版推荐分类包括：

- 全部 / All
- Python
- 深度学习 / Deep Learning
- PyTorch
- AutoDL
- Mac
- Linux
- Conda
- Git
- 常用命令 / Common Commands
- 报错解决 / Error Solutions
- 项目经验 / Project Experience
- 论文笔记 / Paper Notes

## 当前阶段

当前已实现到 Stage 8：数据安全、数据库路径、备份与升级机制整理。

当前应用已经具备 PySide6 主窗口、SQLite `cards` 数据层、正式知识卡片 CRUD、Markdown 预览、普通关键词搜索、草稿区、分类/标签输入体验优化，以及基础数据安全机制。

## 数据存储位置

开发环境和未来打包后的 macOS App 统一使用同一个真实用户数据库路径：

```text
~/Library/Application Support/computer_knowledge_app/knowledge.db
```

真实用户数据库不放在项目 `data/` 目录里，不放在 `.app` 内部，也不应提交到 Git。这样升级或替换 App 本体时，只会替换程序文件，不会覆盖用户的 SQLite 数据库。

App 启动初始化数据库时，如果以下目录不存在，会自动创建：

```text
~/Library/Application Support/computer_knowledge_app/
~/Library/Application Support/computer_knowledge_app/backups/
```

如需临时指定数据库路径，可以设置环境变量：

```text
COMPUTER_KNOWLEDGE_APP_DB_PATH=/path/to/knowledge.db
```

## 数据库版本

数据库使用 `app_meta` 表记录应用元信息。

当前 schema 版本：

```text
schema_version = 1
```

App 启动初始化数据库时会检查 `app_meta.schema_version`。未来如果需要升级数据库结构，应按版本号逐步执行迁移函数，并在迁移前自动备份旧数据库。

## 备份方式

默认备份目录：

```text
~/Library/Application Support/computer_knowledge_app/backups/
```

备份文件是 SQLite 数据库副本，文件名包含时间戳和备份原因。当前服务层已提供手动备份函数：

```python
from src.services.data_safety_service import create_manual_backup

backup_path = create_manual_backup()
```

可以运行简单脚本验证备份和导出流程：

```bash
conda activate computer_knowledge_app
python scripts/test_backup_export.py
```

脚本使用临时数据库和临时目录，不会修改真实用户数据。

## Markdown 导出

当前支持将正式知识卡片导出为 Markdown 文件。导出范围只包含：

```text
is_draft = 0
```

草稿卡片不会被导出。每个 Markdown 文件包含：

- 标题
- 用途场景
- 分类
- 标签
- 摘要
- 创建时间
- 更新时间
- 正文

服务层函数：

```python
from src.services.data_safety_service import export_formal_cards_to_markdown

paths = export_formal_cards_to_markdown("/path/to/export_dir")
```
