# AGENTS.md

## 1. Project Positioning

This project is a local macOS desktop application for building a personal computer learning knowledge base.

The target user is a beginner or early-stage computer science learner who wants to record, organize, search, and review knowledge and experience encountered while learning computer science, including but not limited to:

- computer science terminology
- Python learning notes
- deep learning fundamentals
- PyTorch example code
- terminal commands
- macOS usage tips
- AutoDL environment setup
- conda / pip / tmux / git usage
- error messages and solutions
- project practice experience
- paper reading notes
- draft titles for knowledge cards that the user wants to complete later

This project is not a web application.  
This project is not an AI chatbot.  
This project is not a cloud-sync note-taking app.  
Version 1 should prioritize being simple, stable, local, and easy to search.

---

## 2. Technology Stack

This project uses the following technology stack:

- Python
- PySide6, for developing the macOS desktop GUI
- SQLite, for local data storage
- Markdown, for storing knowledge card content

Do not change the technology stack unless the user explicitly requests it.

Do not convert this project into:

- Flask project
- Django project
- FastAPI project
- Electron project
- web frontend project
- cloud-based application

---

## 3. Core Goals

The core goal of this application is to help the user quickly record and later retrieve personal learning knowledge and troubleshooting experience.

The most important goals for Version 1 are:

1. The user can easily create knowledge cards.
2. Data can be safely stored in a local SQLite database.
3. The user can search by title, tags, category, summary, keywords, and content.
4. When viewing a completed knowledge card, the default display should be Markdown preview mode.
5. Markdown source text should only be shown after the user clicks Edit.
6. Code blocks should be clearly displayed for easy reading and copying.
7. The app should support a Drafts area at the bottom of the left sidebar for quickly recording knowledge-card titles to complete later.
8. Drafts are not a separate task system. A draft is simply an incomplete knowledge card.
9. Version 1 should remain simple and reliable, without adding too many complex features.

---

## 4. Main UI Structure

Version 1 should focus on one main page:

```text
Knowledge Base Main Page
```

The knowledge base main page should use a three-column layout:

```text
Left: categories + drafts
Middle: knowledge card list
Right: card preview / editor
```

The top area should include:

- App name: Personal Computer Knowledge Base
- Current page indicator: Knowledge Base
- Search box: search title, tags, and content
- New Card button
- Import button
- User / settings entry

Version 1 does not need a separate “To-Complete” page.  
Version 1 does not need a separate “Favorites” feature.  
Version 1 does not need a “Common Tags” section in the left sidebar.

---

## 5. Knowledge Base Module

The knowledge base module stores completed and organized knowledge cards.

Knowledge cards should not be strictly separated into “concept explanation cards”, “code template cards”, or “error solution cards”.

Each knowledge card should be understood as:

```text
A complete record around one topic.
```

A knowledge card may contain:

- text explanations
- example code
- terminal commands
- error messages
- solution steps
- notes and caveats
- project experience
- related knowledge
- source links

For example:

```text
What is MLP, and how is it usually written in PyTorch?
```

This card may contain:

- a conceptual explanation of MLP
- the basic structure of MLP
- a minimal PyTorch code example
- the role of each line of code
- input and output dimension notes
- related knowledge points

Another example:

```text
How to fix “zsh: command not found: conda” in macOS Terminal
```

This card may contain:

- the original error message
- the cause of the problem
- commands for checking the environment
- commands for solving the problem
- important notes

---

## 6. Draft Design

Version 1 should not include a separate “to-complete list” page.

Instead, add a Drafts area at the bottom of the left sidebar on the knowledge base main page.

Drafts are used to quickly record:

```text
A title that the user wants to complete into a knowledge card later.
```

Examples:

```text
What is CUDA OOM?
What is the difference between conda and pip?
Why can tmux keep running in the background?
What is PATH in macOS?
What is the difference between MLP and CNN?
```

Drafts should not require complex fields.  
Drafts should not have a separate detail page.  
Drafts should not have priority.  
Drafts should not have task status.  
Drafts should not use “completed / not completed” task-management logic.

A draft is simply an incomplete knowledge card.

When the user enters a title in the Drafts area, the system should create a draft card.  
When the user later clicks a draft title, the app should directly open the card editor on the right side so the user can continue completing the card.

After the user completes the card and saves it as a formal knowledge card, the card should no longer appear in the Drafts area. It should appear in the normal knowledge card list instead.

---

## 7. Knowledge Card Data Model

Version 1 knowledge cards should use the following fields:

```text
id
title
scenario
category
tags
summary
content
keywords
source
is_draft
created_at
updated_at
```

Field meanings:

| Field | Meaning |
|---|---|
| `id` | Unique card ID |
| `title` | Card title |
| `scenario` | Usage scenario |
| `category` | Category |
| `tags` | Tags |
| `summary` | One-sentence summary |
| `content` | Raw Markdown content |
| `keywords` | Additional search keywords |
| `source` | Source link or source note |
| `is_draft` | Whether the card is a draft |
| `created_at` | Creation time |
| `updated_at` | Last update time |

`scenario` may include:

```text
Knowledge Point
Problem Solving
Workflow
Common Commands
Project Experience
Software Tip
Paper Note
Other
```

Meaning of `is_draft`:

```text
is_draft = 1: draft card, only a temporary title or incomplete content has been recorded
is_draft = 0: formal knowledge card, shown in the normal knowledge card list by default
```

Do not add the following fields in Version 1:

```text
status
mastery_status
learning_status
mastered_or_not
difficulty_level
review_status
is_favorite
favorite_status
```

Reasons:

1. This app is for personal use and does not need complex mastery tracking.
2. Marking something as “mastered” now does not mean the user will not forget it later.
3. A personal knowledge base does not need a Favorites feature; search and categories are enough.
4. These fields increase the burden of data entry.
5. Version 1 should prioritize recording, saving, searching, previewing, and editing.

---

## 8. Category Design

The left sidebar category area is used for broad knowledge-domain filtering.

Recommended Version 1 categories:

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

Category meanings:

- `All`: show all formal knowledge cards.
- `Deep Learning`: neural networks, model structures, training, and inference.
- `PyTorch`: PyTorch code, APIs, errors, and training experience.
- `AutoDL`: server rental, environment setup, training and inference workflows.
- `Mac`: macOS operations, terminal usage, shortcuts.
- `Linux`: server commands and Linux usage.
- `Conda`: environment management, package installation, initialization issues.
- `Git`: Git and GitHub usage.
- `Common Commands`: tmux, ffmpeg, scp, conda, and similar commands.
- `Error Solutions`: error messages and solutions.
- `Project Experience`: concrete project practice records.
- `Paper Notes`: paper reading, model analysis, and method summaries.

Version 1 does not need a separate “Common Tags” section in the left sidebar.  
The user will mainly use the top search box and categories for retrieval.

---

## 9. Markdown Requirements

Knowledge card content must be stored as raw Markdown text.

For formal knowledge cards, the default viewing state should be Markdown preview mode.

Basic interaction flow:

```text
Open a formal card
→ Show Markdown preview by default
→ Click “Edit”
→ Show raw Markdown source
→ Click “Save”
→ Save content and return to preview mode
```

If the user clicks “Cancel”, discard the current changes and return to preview mode.

Draft cards behave differently:

```text
Click a draft title
→ Directly enter card edit mode
→ The user completes category, tags, summary, content, and other information
→ Save as a formal card
→ is_draft changes from 1 to 0
→ The card enters the formal knowledge base
```

Markdown preview should support at least:

- headings
- paragraphs
- ordered lists
- unordered lists
- code blocks
- inline code
- links
- blockquotes
- simple tables

Code blocks are a key feature of this project.

The user will frequently record:

- Python code
- Bash commands
- conda commands
- tmux commands
- git commands
- ffmpeg commands
- LaTeX code
- error logs
- configuration files

Code blocks should be clearly displayed and use a monospaced font.

Version 1 only needs to display code blocks clearly.  
Future versions may support:

- syntax highlighting
- one-click copy button in the top-right corner of each code block
- Markdown export
- PDF export

Do not overcomplicate Version 1 for advanced Markdown features.

---

## 10. UI Design Principles

The application UI should be simple, clear, and stable.

The knowledge base main page should use a three-column layout:

```text
Left: categories + drafts
Middle: knowledge card list
Right: card preview / editor
```

### 10.1 Top Area

The top area should contain:

- App name: Personal Computer Knowledge Base
- Current page indicator: Knowledge Base
- Search box: search title, tags, and content
- New Card button
- Import button
- User / settings entry

Do not add complex top-level page switching.  
Version 1 does not need a separate “To-Complete” top navigation tab.

### 10.2 Left Area

The left area should contain:

```text
Categories
Drafts
```

The left area should not contain:

```text
Common Tags
Favorites
```

The category area is used to filter formal knowledge cards.  
The Drafts area is used to quickly record and open incomplete draft cards.

The Drafts area should be placed at the bottom of the left sidebar and should be presented as a lightweight list.

The Drafts area should contain at least:

- Title: Drafts
- Draft count
- Quick input: quickly write down a title
- Draft title list

Each draft item should only display a short title.

Example:

```text
Drafts 5
[Quickly write down a title...]

What is CUDA OOM?
What is the difference between conda and pip?
Why can tmux run in the background?
What is PATH in macOS?
```

### 10.3 Middle Area

The middle area displays the knowledge card list.

Each list item should include:

- title
- short summary
- tags
- category / scenario
- updated time

The selected card should have a clear border or background highlight.

### 10.4 Right Area

The right area displays the selected card details.

Formal cards should display Markdown preview by default.

The right detail area should display:

- title
- scenario
- category
- tags
- one-sentence summary
- Markdown preview area or editor area
- Edit button
- Delete button

The right detail area does not need a Favorite button.

Do not turn the UI into a complex dashboard.  
Do not add complex interactions that are unnecessary for Version 1.  
Version 1 should prioritize clear functions and smooth basic operation.

---

## 11. Search Requirements

Version 1 should support keyword search over:

- title
- summary
- tags
- keywords
- content
- category
- scenario

Version 1 may use normal SQLite `LIKE` search.

Future versions may upgrade to SQLite FTS full-text search.

Recommended search result priority:

```text
Title match first
Tag match second
Summary / keyword match third
Content match last
```

Do not add semantic search, AI search, vector database, or other complex search systems in Version 1 unless explicitly requested by the user.

---

## 12. Database Requirements

This project uses SQLite as the local database.

Version 1 can start with only one core table:

```text
cards
```

Drafts are also knowledge cards, distinguished by `is_draft = 1`.

Version 1 should not create separate complex tables such as:

```text
todos table
to_complete table
favorites table
```

Do not over-normalize the database in Version 1.

Tags may be stored as comma-separated text in Version 1.  
Categories may also be stored as text fields.

Future versions may introduce:

```text
tags table
categories table
attachments table
full-text search table
database migration mechanism
```

Before changing the database schema, explain the reason and impact first.

Do not delete fields without permission.  
Do not clear data without permission.  
Do not overwrite the user’s real database.

Use sample data or a test database for testing.

---

## 13. Recommended Directory Structure

Recommended project structure:

```text
computer_knowledge_app/
├── AGENTS.md
├── README.md
├── requirements.md
├── database_design.md
├── ui_design.md
├── development_plan.md
├── testing_plan.md
├── changelog.md
├── src/
│   ├── main.py
│   ├── app/
│   ├── ui/
│   ├── db/
│   ├── models/
│   ├── services/
│   └── utils/
├── tests/
├── docs/
├── data/
├── backups/
├── assets/
└── .gitignore
```

The structure may be adjusted slightly if there is a good reason.  
Do not introduce unnecessary complex structure.

---

## 14. Development Principles

Follow these principles during development:

1. Prioritize simplicity and stability in Version 1.
2. Implement one small feature at a time.
3. Do not add features outside the current task without permission.
4. Do not perform large unrelated refactors.
5. Do not change the technology stack.
6. Do not introduce unnecessary heavy dependencies.
7. Prefer clear, readable, maintainable code.
8. Keep UI code, database code, and business logic reasonably separated.
9. Explain what changed after each modification.
10. When unsure, choose the simpler and safer implementation.

---

## 15. Data Safety Rules

Do not delete or overwrite the following directories without explicit user permission:

```text
data/
backups/
attachments/
exports/
```

Do not commit the real user database.  
Do not commit the user’s private notes.  
Do not commit large generated files.  
Do not modify `.gitignore` in a way that causes private data to enter version control.

If a task may affect existing data, explain the risk first.

---

## 16. Version 1 Scope

Version 1 should include:

1. PySide6 main window.
2. Three-column knowledge base layout.
3. Left-side category area.
4. Left-bottom Drafts area.
5. SQLite database initialization.
6. Create, view, edit, and delete knowledge cards.
7. Quick creation of draft cards.
8. Clicking a draft title opens the card editor.
9. Draft cards can be saved as formal knowledge cards.
10. Markdown content saving.
11. Markdown preview mode.
12. Edit / Save / Cancel flow.
13. Search by title, tags, summary, keywords, and content.
14. Category filtering.
15. Local data persistence.

Version 1 should not include:

- AI assistant
- cloud sync
- login system
- user account system
- web version
- mobile version
- semantic search
- PDF export
- complex plugin system
- Favorites feature
- separate To-Complete page
- Common Tags sidebar
- complex task management system

---

## 17. Suggested Development Stages

Develop the project in the following stages.

### Stage 0: Project Documentation and Skeleton

Create documentation, directory structure, and basic project files.  
Do not implement business logic yet.

### Stage 1: Minimal PySide6 Window

Create a runnable PySide6 main window.  
Only implement the basic three-column layout.

### Stage 2: SQLite Data Layer

Implement database initialization and basic CRUD operations.  
Version 1 should use `cards` as the core table.  
Drafts should be distinguished by the `is_draft` field.

### Stage 3: Knowledge Card CRUD

Connect the UI and database to implement knowledge card creation, viewing, editing, and deletion.

### Stage 4: Markdown Preview and Edit Mode

Implement switching between Markdown preview mode and edit mode.  
Formal cards should open in preview mode by default.  
Draft cards should open in edit mode by default.

### Stage 5: Search

Implement keyword search.  
Search should cover title, tags, summary, keywords, content, category, and scenario.

### Stage 6: Drafts

Implement the Drafts area at the bottom of the left sidebar.

This includes:

- quick draft title input
- draft card creation
- draft list display
- clicking a draft opens edit mode
- saving a draft as a formal knowledge card

### Stage 7: UX Improvements

Add delete confirmation, layout improvements, search result sorting, code block display improvements, and other UX enhancements.

### Stage 8: macOS Packaging

After the core functions are stable, consider packaging the app as a macOS application.

---

## 18. Testing Requirements

For each completed feature, provide a simple verification method.

Important checks include:

1. The application can start normally.
2. A knowledge card can be created.
3. A knowledge card can be edited.
4. There is confirmation before deleting a knowledge card.
5. Data still exists after restarting the application.
6. Markdown preview can display headings, lists, and code blocks.
7. Search can find content from titles, tags, and card bodies.
8. A draft title can be quickly created in the left Drafts area.
9. Clicking a draft title opens card edit mode.
10. After a draft is saved as a formal card, it no longer appears in the Drafts area.
11. The formal card appears in the knowledge card list.
12. Tests do not delete real user data.

If automated tests are added, keep them simple and focused.

---

## 19. Task Completion Report Format

After completing each task, report:

1. What was implemented.
2. Which files were modified.
3. How to run the application.
4. How to verify the feature.
5. Whether there are unfinished parts or risks.

Do not claim a feature is fully complete without testing it or clearly explaining what remains untested.

---

## 20. Communication Style

Use Chinese when explaining changes to the user.

Explanations should be clear, specific, and suitable for a beginner.

Avoid unnecessary jargon.  
If technical terms must be used, explain them in simple language.

Each explanation should include:

- what was done
- why it was done this way
- what the next step should be
- whether there are any risks

The user is a beginner, so responses should be practical, step-by-step, and should not assume the user is already familiar with complex development workflows.
