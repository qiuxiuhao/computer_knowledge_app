# ui_design.md

## 1. Document Purpose

This document describes the UI design, page structure, interaction behavior, and visual style of the “Personal Computer Knowledge Base” macOS desktop application.

This project uses:

```text
Python + PySide6 + SQLite + Markdown
```

The design goals for Version 1 are:

```text
simple
clear
stable
beginner-friendly
easy to search
easy to record
easy to view Markdown previews
easy to continue completing draft cards
```

This project is not a complex note-taking app, and it is not a task management app.  
Version 1 should not pursue fancy visual effects. The priority is clear functionality, smooth operation, and easy future extension.

---

## 2. Overall UI Positioning

The application is positioned as:

```text
personal computer learning knowledge base
personal error-solution record base
personal command template base
personal project experience base
personal paper note base
personal draft-card holding area
```

Main user scenarios include:

1. Recording computer science terminology.
2. Recording Python / PyTorch / deep learning knowledge.
3. Recording AutoDL, Conda, Linux, and Mac environment setup experience.
4. Recording common commands.
5. Recording errors and solutions.
6. Recording paper reading notes.
7. Temporarily writing down titles of knowledge cards to complete later.
8. Quickly retrieving previously recorded content through search.

---

## 3. Version 1 UI Scope

Version 1 should only include one core page:

```text
Knowledge Base Main Page
```

Version 1 should not include:

```text
separate To-Complete page
Favorites page
Common Tags sidebar
complex task management page
AI Q&A page
cloud sync page
login page
```

The Drafts feature should be placed directly at the bottom of the left sidebar on the knowledge base main page.

---

## 4. Overall Layout

The knowledge base main page uses a three-column layout.

```text
┌──────────────────────────────────────────────────────────────┐
│ Top bar: app name / search box / new card / import / user     │
├───────────────┬─────────────────────┬────────────────────────┤
│ Left sidebar   │ Middle card list     │ Right preview / editor  │
│ Categories     │ Knowledge cards      │ Markdown preview/editor │
│ Drafts         │                     │                        │
└───────────────┴─────────────────────┴────────────────────────┘
```

Recommended width ratio:

```text
Left sidebar: about 18% - 22%
Middle list: about 28% - 32%
Right content area: about 46% - 54%
```

On wider screens, the right content area should take the largest space because most of the user's time will be spent reading and editing cards.

---

## 5. Top Bar Design

The top bar is located at the top of the window.

The top bar contains:

1. macOS-style window buttons.
2. App icon.
3. App name.
4. Current page indicator: Knowledge Base.
5. Search box.
6. New Card button.
7. Import button.
8. User / settings entry.

### 5.1 Top Bar Structure

```text
┌──────────────────────────────────────────────────────────────┐
│ ● ● ●  Icon  Personal Computer Knowledge Base   Knowledge Base   [Search]   + New Card  Import  User │
└──────────────────────────────────────────────────────────────┘
```

### 5.2 App Name

Display:

```text
Personal Computer Knowledge Base
```

In the Chinese UI, display:

```text
个人计算机知识库
```

### 5.3 Current Page Indicator

Display:

```text
Knowledge Base
```

In the Chinese UI, display:

```text
知识库
```

The current page should be highlighted with a blue underline or blue text.

Version 1 does not need a top-level “To-Complete” tab.  
Drafts do not exist as a separate page.

### 5.4 Search Box

The search box should occupy the main center area of the top bar.

Placeholder text:

```text
Search title, tags, and content...
```

In the Chinese UI, display:

```text
搜索标题、标签、正文...
```

Search scope includes:

```text
title
summary
tags
keywords
content
category
scenario
```

Search behavior:

1. Typing keywords should trigger search in real time or after pressing Enter.
2. Search results should appear in the middle knowledge card list.
3. When the search box is empty, the list should return to the current category's card list.
4. Version 1 may use normal SQLite LIKE search.
5. A later version may upgrade to SQLite FTS full-text search.

### 5.5 New Card Button

Button text:

```text
+ New Card
```

In the Chinese UI, display:

```text
+ 新建卡片
```

Click behavior:

1. Open the new-card editor on the right side.
2. This is not a draft by default. It is the normal formal-card creation flow.
3. The user fills in title, category, tags, summary, and Markdown content.
4. After saving, the card enters the formal knowledge card list.

### 5.6 Import Button

Button text:

```text
Import
```

In the Chinese UI, display:

```text
导入
```

Version 1 may keep this button as a placeholder and does not need to implement complex import functionality immediately.

If not implemented yet, clicking it may show:

```text
Import will be supported in a future version.
```

In the Chinese UI:

```text
导入功能将在后续版本支持。
```

### 5.7 User / Settings Entry

The top-right corner should display a simple user or settings icon.

Version 1 may use this as a placeholder.

Future versions may include:

1. Database path settings.
2. Backup settings.
3. Theme settings.
4. About page.

---

## 6. Left Sidebar Design

The left sidebar contains two parts:

```text
Categories
Drafts
```

The left sidebar does not contain:

```text
Favorites
Common Tags
```

Reasons:

1. This is a personal knowledge base, so a Favorites feature is not necessary for Version 1.
2. The user mainly retrieves content through search and categories.
3. Common tags take up sidebar space, and the user is more likely to search directly.
4. Drafts are more important than Favorites and should be placed at the bottom of the left sidebar.

---

## 7. Left Sidebar: Category Area

The category area is located in the upper part of the left sidebar.

Title:

```text
Categories
```

In the Chinese UI, display:

```text
分类
```

Recommended category list:

```text
All
Python
Deep Learning
PyTorch
AutoDL
Mac
Linux
Conda
Git
Common Commands
Error Solutions
Project Experience
Paper Notes
```

In the Chinese UI, display:

```text
全部
Python
深度学习
PyTorch
AutoDL
Mac
Linux
Conda
Git
常用命令
报错解决
项目经验
论文笔记
```

### 7.1 Category Item Content

Each category item should contain:

1. Icon.
2. Category name.
3. Count.

Example:

```text
All                 119
Python               22
Deep Learning         18
PyTorch              14
AutoDL                9
Mac                  16
Linux                15
Conda                11
Git                  12
Common Commands      20
Error Solutions      21
Project Experience   13
Paper Notes           8
```

Chinese UI example:

```text
全部        119
Python      22
深度学习     18
PyTorch     14
AutoDL       9
Mac         16
Linux       15
Conda       11
Git         12
常用命令     20
报错解决     21
项目经验     13
论文笔记      8
```

### 7.2 Selected Category State

The selected category should use a light blue background and blue text.

For example, when “Deep Learning” is selected:

```text
[blue highlight] Deep Learning 18
```

Chinese UI:

```text
[蓝色高亮] 深度学习 18
```

### 7.3 Category Click Behavior

When the user clicks a category:

1. The middle card list should only show formal cards under that category.
2. The Drafts area should not be affected by category filtering.
3. If the currently selected card does not belong to the selected category, the right detail area may be cleared or automatically show the first card in the filtered list.

### 7.4 All Category

When the user clicks “All”:

1. The middle list should show all formal knowledge cards.
2. Draft cards should not appear in the middle list.
3. Draft cards should only appear in the left Drafts area.

---

## 8. Left Sidebar: Drafts Area

The Drafts area is located at the bottom of the left sidebar.

It is used to quickly record titles that the user wants to complete into full knowledge cards later.

Drafts are not separate tasks.  
Drafts are not to-do items.  
A draft is essentially:

```text
a knowledge card with is_draft = 1
```

### 8.1 Drafts Area Structure

Recommended structure:

```text
Drafts                         5
[Quickly write down a title...]

What is CUDA OOM?
What is the difference between conda and pip?
Why can tmux keep running in the background?
What is PATH in macOS?
```

Chinese UI:

```text
草稿                         5
[快速记下一个标题...]

什么是 CUDA OOM
conda 和 pip 的区别
tmux 为什么能后台运行
macOS 里的 PATH 是什么
```

### 8.2 Drafts Title

Display:

```text
Drafts
```

Chinese UI:

```text
草稿
```

Show the draft count on the right:

```text
5
```

### 8.3 Draft Quick Input

Input placeholder:

```text
Quickly write down a title...
```

Chinese UI:

```text
快速记下一个标题...
```

Interaction behavior:

1. The user enters a title.
2. Pressing Enter or clicking Add creates a draft card.
3. A draft card only requires a title to be created.
4. The new draft should appear at the top of the Drafts list.

### 8.4 Draft List Items

Each draft list item only displays a short title.

Examples:

```text
What is CUDA OOM?
What is the difference between conda and pip?
Why can tmux keep running in the background?
What is PATH in macOS?
```

Chinese UI:

```text
什么是 CUDA OOM
conda 和 pip 的区别
tmux 为什么能后台运行
macOS 里的 PATH 是什么
```

Each row may include:

1. Document icon.
2. Draft title.
3. Optional delete button.

### 8.5 Draft Click Behavior

When the user clicks a draft title:

1. The middle knowledge card list may remain unchanged.
2. The right side opens the draft card.
3. The right side directly enters edit mode.
4. The user can complete category, tags, summary, content, and other information.
5. After the user saves, the card changes from draft to formal card.
6. `is_draft` changes from `1` to `0`.
7. The draft disappears from the left Drafts area.
8. The new card enters the middle knowledge card list.

### 8.6 Draft Deletion

Drafts can be deleted.

A confirmation dialog is recommended before deletion:

```text
Are you sure you want to delete this draft?
```

Chinese UI:

```text
确定删除这个草稿吗？
```

Reason:

Even though a draft may contain little content, it may still represent something the user wanted to learn later. Accidental deletion would lose that reminder.

---

## 9. Middle Column: Knowledge Card List

The middle column displays the formal knowledge card list.

Title:

```text
Knowledge Cards
```

Chinese UI:

```text
知识卡片
```

Show the count on the right:

```text
18 items
```

Chinese UI:

```text
共 18 条
```

### 9.1 List Item Content

Each card list item should display:

1. Title.
2. Short summary.
3. Tags.
4. Category.
5. Usage scenario.
6. Updated time.

Example:

```text
What is MLP, and how is it usually written in PyTorch?

Introduces the definition and structure of MLP and a minimal PyTorch implementation.

MLP  PyTorch  Neural Network  Fully Connected Layer

Deep Learning · Knowledge Point          Updated 2024-05-12 10:30
```

Chinese UI example:

```text
MLP 是什么，以及 PyTorch 中一般怎么写

介绍 MLP 的定义、结构和在 PyTorch 中的最小实现方式。

MLP  PyTorch  神经网络  全连接层

深度学习 · 知识点          更新于 2024-05-12 10:30
```

### 9.2 List Item Visual Style

Card list items should use:

1. White background.
2. Rounded rectangle.
3. Subtle shadow.
4. Proper whitespace.
5. Selected item with blue border or light blue background.

### 9.3 Selected Card

When the user clicks a card in the list:

1. The card should be highlighted in the middle list.
2. The right side should display the card details.
3. Formal cards should open in Markdown preview mode by default.

### 9.4 Draft Cards Should Not Appear in the Formal List

By default:

```text
The middle knowledge card list should only show cards with is_draft = 0.
```

Draft cards should only appear in the left Drafts area.

---

## 10. Right Column: Card Detail Area

The right column displays the currently selected card details.

Formal cards should display Markdown preview by default.

### 10.1 Right Top Content

The right top area displays:

1. Card title.
2. Edit button.
3. Delete button.

Do not display a Favorite button.

Example:

```text
What is MLP, and how is it usually written in PyTorch                    Edit   Delete
```

Chinese UI:

```text
MLP 是什么，以及 PyTorch 中一般怎么写                    编辑   删除
```

### 10.2 Metadata Area

Below the title, display metadata.

Include:

```text
Scenario: Knowledge Point
Category: Deep Learning
Tags: MLP / PyTorch / Neural Network / Fully Connected Layer
One-sentence summary: MLP is a neural network structure composed of multiple fully connected layers and activation functions.
```

Chinese UI:

```text
用途场景：知识点
分类：深度学习
标签：MLP / PyTorch / 神经网络 / 全连接层
一句话总结：MLP 是由多个全连接层和激活函数组成的神经网络结构。
```

### 10.3 Markdown Preview Area

Below the metadata area, display Markdown preview content.

Example structure:

```text
1. Usage Scenario

2. Basic Structure

3. Minimal PyTorch Code

4. Code Explanation

5. Notes
```

Chinese UI:

```text
一、使用场景

二、基本结构

三、PyTorch 最小代码

四、代码解释

五、注意事项
```

Code blocks should have a clear visual style.

Example code block:

```python
import torch.nn as nn

model = nn.Sequential(
    nn.Linear(784, 128),
    nn.ReLU(),
    nn.Linear(128, 10)
)
```

Future versions may support a button at the top-right corner of each code block:

```text
Copy
```

Chinese UI:

```text
复制
```

If implementation cost is high in Version 1, it is acceptable to only display code blocks clearly without a copy button.

---

## 11. Right Column: Edit Mode

After the user clicks “Edit”, the right side enters edit mode.

Edit mode contains:

1. Title input.
2. Scenario selector.
3. Category selector.
4. Tags input.
5. One-sentence summary input.
6. Markdown content editor.
7. Save button.
8. Cancel button.

### 11.1 Formal Card Editing Flow

Formal card flow:

```text
Open formal card
→ Show preview mode by default
→ Click Edit
→ Enter edit mode
→ Modify content
→ Click Save
→ Save and return to preview mode
```

### 11.2 Draft Card Editing Flow

Draft card flow:

```text
Click draft title in the left sidebar
→ Right side directly enters edit mode
→ Complete the card information
→ Click Save as Formal Card
→ is_draft = 0
→ Remove from Drafts area
→ Add to formal knowledge card list
```

Draft cards do not need to show preview mode first.

---

## 12. Delete Interaction

Before deleting a formal card, confirmation is required.

Prompt text:

```text
Are you sure you want to delete this knowledge card?
```

Chinese UI:

```text
确定删除这张知识卡片吗？
```

Before deleting a draft, confirmation is also required.

Prompt text:

```text
Are you sure you want to delete this draft?
```

Chinese UI:

```text
确定删除这个草稿吗？
```

After deletion:

1. Delete the corresponding record from the database.
2. Update the middle list or the left Drafts area.
3. If the deleted item is currently displayed on the right side, clear the right area or show the next card.

---

## 13. Search Interaction

The search box is located in the top bar.

Search scope:

```text
title
summary
tags
keywords
content
category
scenario
```

Chinese description:

```text
标题
摘要
标签
关键词
正文
分类
用途场景
```

### 13.1 Search Behavior

After the user enters keywords:

1. The middle list displays matching formal cards.
2. The Drafts area continues to show the draft list.
3. If there are no search results, the middle area shows an empty-state message.
4. Version 1 does not need to search drafts. A later version may consider draft search.

### 13.2 Empty Search Result State

When there are no matching results, the middle list should display:

```text
No related knowledge cards found.
```

Chinese UI:

```text
没有找到相关知识卡片
```

Optional hint:

```text
Try another keyword, or create a new card.
```

Chinese UI:

```text
可以尝试换一个关键词，或新建一张卡片。
```

---

## 14. Empty States

### 14.1 No Knowledge Cards

When there are no formal cards, the middle column displays:

```text
No knowledge cards yet.
Click “New Card” to record your first knowledge point.
```

Chinese UI:

```text
还没有知识卡片
点击“新建卡片”开始记录你的第一个知识点。
```

### 14.2 No Drafts

When there are no drafts, the Drafts area displays:

```text
No drafts yet.
You can quickly write down a title to complete later.
```

Chinese UI:

```text
暂无草稿
可以快速记下一个以后想补充的标题。
```

### 14.3 No Selected Card

When no card is selected, the right side displays:

```text
Select a knowledge card to view details.
```

Chinese UI:

```text
请选择一张知识卡片查看详情
```

Or:

```text
Click a draft title on the left to continue completing an unfinished card.
```

Chinese UI:

```text
点击左侧草稿标题，可以继续补充未完成卡片。
```

---

## 15. Visual Style

Version 1 visual style requirements:

```text
light theme
blue accent color
rounded cards
subtle shadows
clear sections
comfortable for long reading sessions
no excessive decoration
```

### 15.1 Main Color

Use blue as the main accent color.

Example:

```text
Main blue: #2563EB
Light blue background: #EFF6FF
Blue border: #3B82F6
```

### 15.2 Background Colors

Recommended:

```text
Window background: #F8FAFC
Card background: #FFFFFF
Divider line: #E5E7EB
Sidebar background: #F9FAFB
```

### 15.3 Text Colors

Recommended:

```text
Primary text: #111827
Secondary text: #6B7280
Muted hint text: #9CA3AF
Danger action: #DC2626
```

### 15.4 Button Styles

Primary button:

```text
blue background
white text
rounded corners
```

Normal button:

```text
white background
light gray border
dark text
```

Danger button:

```text
red text
light red border or red icon
```

---

## 16. Fonts and Spacing

### 16.1 Fonts

On macOS, prefer system fonts.

Recommended:

```text
-apple-system
BlinkMacSystemFont
SF Pro Text
Helvetica Neue
Arial
```

Code blocks should use a monospaced font.

Recommended:

```text
SF Mono
Menlo
Monaco
Consolas
monospace
```

### 16.2 Font Size Suggestions

```text
App title: 16 - 18 px
Top navigation: 14 - 15 px
Category item: 14 px
Card title: 15 - 16 px
Card summary: 13 - 14 px
Right article title: 22 - 26 px
Body text: 14 - 15 px
Code block: 13 - 14 px
Auxiliary information: 12 - 13 px
```

### 16.3 Spacing Suggestions

```text
Left sidebar padding: 16 - 20 px
Card list spacing: 12 - 16 px
Card internal padding: 14 - 18 px
Right content area padding: 28 - 40 px
Paragraph spacing: 8 - 12 px
Section spacing: 20 - 28 px
```

---

## 17. PySide6 Implementation Suggestions

Version 1 may use the following PySide6 components.

### 17.1 Main Window

Possible components:

```text
QMainWindow
QWidget
QVBoxLayout
QHBoxLayout
QSplitter
```

Use `QSplitter` to implement a resizable three-column layout.

### 17.2 Left Sidebar

Possible components:

```text
QWidget
QVBoxLayout
QListWidget
QScrollArea
QLineEdit
QPushButton
```

The category list can initially use `QListWidget`.  
The draft list can also initially use `QListWidget`.

### 17.3 Middle Card List

Possible components:

```text
QListWidget
QListView
QScrollArea + custom card widget
```

For Version 1, `QListWidget` with custom item widgets is acceptable.

### 17.4 Right Detail Area

Preview mode may initially use:

```text
QTextBrowser
```

Edit mode may use:

```text
QTextEdit
QLineEdit
QComboBox
QPushButton
```

For Markdown preview, Version 1 can use Qt's built-in Markdown support or convert Markdown to HTML and display it.

If future versions need better code highlighting and copy buttons, the preview may be upgraded to:

```text
Markdown → HTML → QWebEngineView
```

Do not overcomplicate Version 1.

---

## 18. Codex Development Notes

When asking Codex to implement the UI, follow these requirements:

1. First implement static UI layout without connecting to the database.
2. Use mock data to populate categories, drafts, card list, and right preview.
3. Do not implement full business logic at the beginning.
4. Do not add a Favorites feature.
5. Do not add a separate To-Complete page.
6. Do not add a Common Tags sidebar.
7. Do not add a complex task management system.
8. Keep the main UI as a three-column layout.
9. Drafts must be located at the bottom of the left sidebar.
10. Formal cards should open in preview mode by default, and draft cards should open in edit mode by default.

Recommended Codex task prompt:

```text
Please read AGENTS.md and ui_design.md first.

This task only implements the static UI layout. Do not connect to the database, do not implement real search, and do not implement real Markdown rendering.

Requirements:
1. The top area has the app name, search box, New Card button, and Import button.
2. The left side has a category area and a bottom Drafts area.
3. The left side must not show Favorites or Common Tags.
4. The categories must include Paper Notes.
5. The middle area shows a knowledge card list with mock data.
6. The right area shows the MLP card preview with mock data.
7. The right area only has Edit and Delete buttons. Do not add a Favorite button.
8. The Drafts area includes a quick input field and several draft titles.
9. Keep the interface clean and close to the UI preview image.
```

---

## 19. Version 1 UI Acceptance Criteria

After the Version 1 UI is implemented, it should satisfy:

1. The application can launch normally.
2. The top bar is displayed correctly.
3. The left sidebar shows categories and drafts.
4. The left sidebar does not show Favorites.
5. The left sidebar does not show Common Tags.
6. The category list includes Paper Notes.
7. The middle column displays a knowledge card list.
8. The right column displays card details.
9. The right column does not have a Favorite button.
10. The Drafts area shows a quick input field and a draft title list.
11. The overall layout is three columns.
12. The visual style is close to the confirmed UI preview image.
13. Before database integration, the full UI can still be displayed using mock data.
