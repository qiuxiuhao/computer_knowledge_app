# Changelog

本文档记录项目变更。

## 2026-07-01

### Stage 8 Added

- 新增统一数据库路径管理：开发环境和未来打包环境默认都使用 `~/Library/Application Support/computer_knowledge_app/knowledge.db`。
- App 启动初始化数据库时，会自动创建 `~/Library/Application Support/computer_knowledge_app/` 和 `~/Library/Application Support/computer_knowledge_app/backups/`。
- 新增 `app_meta` 表记录 `schema_version`，当前版本为 `1`。
- App 初始化数据库时会检查 schema 版本，并预留按版本迁移的入口。
- 新增迁移前自动备份机制，未来数据库升级前会先复制旧数据库。
- 新增数据库备份函数，默认备份目录为 `~/Library/Application Support/computer_knowledge_app/backups/`。
- 新增服务层手动备份函数。
- 新增正式知识卡片 Markdown 导出函数，导出内容包含标题、用途场景、分类、标签、摘要、创建时间、更新时间和正文。
- 新增 `scripts/test_backup_export.py`，用于临时数据库下验证备份和 Markdown 导出流程。
- 更新 README，说明数据存储位置、备份方式和升级原则。
- 更新 `.gitignore`，避免提交数据库、备份文件和打包产物。

### Stage 8 Notes

- 未修改 `cards` 表现有字段。
- 未添加收藏功能、独立待补充页面、常用标签侧栏、`todos` 表或 `favorites` 表。
- 未实现 AI、云同步、Web 功能或 PyInstaller 打包。
- 未实现完整 Markdown 导入功能。

### Stage 7 Added

- 编辑模式中的分类字段改为固定候选 + 可手动输入的下拉选择框。
- 分类下拉框默认包含 Python、深度学习、PyTorch、AutoDL、Mac、Linux、Conda、Git、常用命令、报错解决、项目经验、论文笔记和其他。
- 分类和用途场景下拉框右侧新增明确可见的下拉箭头区域，避免看起来像普通输入框。
- 标签输入框新增自动补全，候选来自数据库中已有卡片的 `cards.tags` 字段。
- 新建和更新卡片时会自动清理标签：支持中文逗号和英文逗号、去除首尾空格、去除空标签、自动去重，并保存为英文逗号分隔格式。

### Stage 7 Notes

- 未修改 `cards` 表结构，标签仍保存到 `cards.tags`。
- 未新建 `tags` 表。
- 未添加收藏功能、独立待补充页面、常用标签侧栏、`todos` 表或 `favorites` 表。

### Stage 6 Added

- 左侧底部草稿输入框支持回车创建草稿。
- 草稿区新增轻量“+”按钮，可点击创建草稿。
- 新草稿只写入 `cards.title` 并设置 `is_draft = 1`。
- 创建草稿后会清空输入框，并立即刷新左侧草稿列表。
- 草稿列表显示所有 `is_draft = 1` 的卡片标题，新草稿显示在顶部。
- 草稿列表每一项新增删除入口，删除前弹出“确定删除这个草稿吗？”确认框。
- 点击草稿标题后，右侧直接进入编辑模式。
- 草稿保存后会变成正式卡片，进入中间正式知识卡片列表，并从草稿区移除。

### Stage 6 Notes

- 未修改 `cards` 表结构。
- 未创建 `todos`、`to_complete` 或 `favorites` 表。
- 未把草稿做成任务管理系统，未添加优先级或完成状态。
- 未添加收藏功能、独立待补充页面、常用标签侧栏、AI、云同步或 Web 功能。

### Stage 5 Added

- 新增普通关键词搜索函数 `search_cards`，使用 SQLite `LIKE` 和参数化查询。
- 搜索范围覆盖正式知识卡片的标题、摘要、标签、关键词、正文、分类和用途场景。
- 搜索结果只包含 `is_draft = 0` 的正式知识卡片，不显示草稿。
- 顶部搜索框输入内容后会刷新中间知识卡片列表，清空后恢复当前分类下的正式卡片列表。
- 左侧分类现在可点击，分类筛选可与搜索组合使用。
- 搜索无结果时，中间列表显示“没有找到相关知识卡片”。

### Stage 5 Notes

- 未修改 `cards` 表结构。
- 未实现 AI 搜索、语义搜索、向量数据库、SQLite FTS、云同步、登录或 Web 功能。
- 未添加收藏功能、独立待补充页面、常用标签侧栏、`todos` 表或 `favorites` 表。

### Stage 4 Added

- 正式知识卡片右侧正文改为 Markdown 预览模式，使用 `markdown` 包转 HTML 后由 `QTextBrowser` 显示。
- Markdown 预览支持标题、段落、列表、行内代码、代码块、引用和简单表格。
- 为代码块、行内代码、引用和表格加入本地 HTML/CSS 样式，代码块使用等宽字体、浅灰背景和圆角边框。
- 编辑模式继续使用 `QTextEdit` 编辑 Markdown 原文，保存后写入 SQLite 并回到预览模式。
- 点击左侧草稿标题后，右侧直接进入编辑模式。
- 草稿保存后会设置 `is_draft = 0`，从草稿区移除并进入正式知识卡片列表。

### Stage 4 Notes

- 未修改 `cards` 表结构。
- 未实现代码块一键复制、复杂代码高亮、复杂搜索或导入功能。
- 未添加收藏功能、独立待补充页面、常用标签侧栏、`todos` 表或 `favorites` 表。

### Stage 3 Added

- App 启动时初始化 `data/knowledge.db`，并在空库时插入符合设计的示例卡片和草稿标题。
- 中间知识卡片列表改为读取 `cards.is_draft = 0` 的正式卡片。
- 左侧草稿区改为读取 `cards.is_draft = 1` 的草稿标题。
- 右侧详情区支持正式卡片预览模式、编辑模式、新建保存、编辑保存和删除确认。
- 编辑保存和删除操作会写回 SQLite 的 `cards` 表。

### Stage 3 Notes

- 本阶段没有实现真实搜索。
- 本阶段没有实现完整 Markdown 高级渲染，正文仍以纯文本方式预览。
- 本阶段没有实现草稿点击转正式卡片。
- 未添加收藏功能、独立待补充页面、常用标签侧栏、`todos` 表、`favorites` 表或 `is_favorite` 字段。

### Stage 2 Added

- 实现 SQLite 数据库初始化函数，默认数据库路径为 `data/knowledge.db`。
- 创建 `cards` 核心表，包含第一版要求的 12 个字段。
- 新增卡片数据模型 `Card`。
- 新增卡片数据访问函数：创建、读取正式卡片、读取草稿、按 ID 读取、更新、删除、草稿转正式卡片。
- 新增示例数据插入函数，方便手动测试数据库层。
- 新增临时数据库单元测试，避免删除或覆盖真实用户数据。

### Stage 2 Notes

- 本次只实现数据库初始化和数据访问层。
- 未将 SQLite 全面连接到当前 PySide6 静态 UI。
- 未实现真实搜索界面交互。
- 未实现 Markdown 预览逻辑。
- 未添加 `todos` 表或 `favorites` 表。

### Stage 1 Added

- 实现 Stage 1 最小 PySide6 静态主窗口。
- 使用三栏布局展示分类、草稿、知识卡片列表和右侧 MLP 卡片预览假数据。
- 顶部区域加入应用名称、当前页面、搜索框、新建卡片、导入按钮和用户 / 设置占位区域。
- 右侧只保留“编辑”和“删除”按钮，不添加收藏按钮。
- 移除手动画出的 macOS 三色窗口按钮、蓝色方框图标、右上角用户头像和下拉尖角。

### Stage 1 Notes

- 本次只实现静态 UI 和假数据展示。
- 未连接 SQLite。
- 未实现真实搜索。
- 未实现真实 Markdown 渲染。
- 未实现真实增删改查。
- 未添加独立待补充页面、收藏功能或常用标签侧栏。

### Stage 0 Added

- 创建项目 README。
- 创建需求说明文档。
- 创建数据库设计文档。
- 创建开发计划文档。
- 创建测试计划文档。
- 创建更新日志。
- 创建 `.gitignore`。
- 创建基础目录结构：
  - `src/`
  - `src/app/`
  - `src/ui/`
  - `src/db/`
  - `src/models/`
  - `src/services/`
  - `src/utils/`
  - `tests/`
  - `docs/`
  - `data/`
  - `backups/`

### Stage 0 Notes

- 本次只完成 Stage 0：项目文档和基础目录。
- 未实现 PySide6 窗口。
- 未实现 SQLite 数据库。
- 未实现真实搜索。
- 未实现 Markdown 预览。
- 未添加收藏功能。
- 未添加独立待补充页面。
- 未添加常用标签侧栏。
