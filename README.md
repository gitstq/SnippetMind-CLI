<div align="center">

# 🧠 SnippetMind-CLI

**AI-Powered Smart Code Snippet Manager with Semantic Search**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-20%2F20%20Passing-brightgreen)](tests/)

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

## English

### 🎉 Introduction

**SnippetMind-CLI** is an intelligent code snippet management tool designed for developers who want to organize, search, and reuse their code efficiently. Unlike traditional snippet managers, SnippetMind leverages AI-powered features like automatic language detection, smart tagging, and semantic search to make your code library truly intelligent.

**Inspiration**: Born from the daily frustration of searching through scattered code files, Stack Overflow bookmarks, and disorganized notes. SnippetMind brings order to chaos with a single, powerful CLI tool.

**Key Differentiators**:
- 🧠 **AI Auto-Analysis**: Automatically detects programming language, generates tags, and suggests descriptions
- 🔍 **Semantic Search**: Full-text search powered by SQLite FTS5 with intelligent ranking
- ⚡ **Zero Configuration**: Works out of the box with sensible defaults
- 🔒 **Privacy First**: All data stored locally in SQLite - nothing leaves your machine

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🧠 **AI Language Detection** | Auto-detects 15+ programming languages from code patterns |
| 🏷️ **Smart Auto-Tagging** | Automatically categorizes snippets by content analysis |
| 🔍 **Full-Text Search** | Lightning-fast search with SQLite FTS5 |
| 📋 **Syntax Highlighting** | Beautiful code display with Rich terminal rendering |
| ⭐ **Favorites** | Mark and quickly access your most-used snippets |
| 📁 **Collections** | Organize snippets into custom collections |
| 📤 **Import/Export** | JSON and Markdown export formats |
| 🎮 **Interactive Mode** | TUI-style interactive snippet management |
| 📊 **Statistics** | Insights into your snippet usage patterns |

**Supported Languages**: Python, JavaScript, TypeScript, Go, Rust, Java, C/C++, Bash, SQL, HTML, CSS, JSON, YAML, Dockerfile, Markdown, and more!

### 🚀 Quick Start

#### Requirements
- Python 3.8 or higher
- pip package manager

#### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/SnippetMind-CLI.git
cd SnippetMind-CLI

# Install dependencies
pip install -r requirements.txt

# Install as a package (optional)
pip install -e .
```

#### Basic Usage

```bash
# Add a new snippet
snippetmind add --title "Hello World" --code "print('hello')" --language python

# Or use the short alias
sm add --title "API Request" --code "import requests" --tags "api,network"

# Search snippets
sm search "hello"

# List all snippets
sm list

# Show snippet with syntax highlighting
sm show 1

# Copy snippet to clipboard
sm copy 1

# Toggle favorite
sm favorite 1

# View statistics
sm stats
```

### 📖 Detailed Usage Guide

#### Adding Snippets

```bash
# From command line
sm add --title "Quick Sort" --code "def quicksort(arr):..." --language python

# From clipboard
sm add --title "From Clipboard" --from-clipboard

# From file
sm add --title "Config" --from-file ./config.py

# With full metadata
sm add --title "Database Query" \
       --code "SELECT * FROM users" \
       --language sql \
       --description "Select all active users" \
       --tags "database,sql,users" \
       --source "https://docs.example.com"
```

#### Searching

```bash
# Basic keyword search
sm search "function"

# Filter by language
sm search "api" --language python

# Semantic search (keyword-based ranking)
sm search "sort algorithm" --semantic
```

#### Managing Collections

```bash
# Create a collection
sm collection create "Web Development" --description "Frontend and backend snippets"

# List collections
sm collection list

# Add snippet to collection
sm collection add 1 1
```

#### Interactive Mode

```bash
# Launch interactive TUI
sm interactive
```

### 💡 Design Philosophy

**Local-First Architecture**: All your snippets are stored in a local SQLite database (`~/.snippetmind/snippets.db`). No cloud dependency, no subscription fees, complete data ownership.

**AI Without the Cloud**: Language detection and tag generation run entirely locally using pattern matching and heuristics. No API keys, no rate limits, no privacy concerns.

**Developer Experience First**: Every command is designed to be intuitive and fast. Syntax highlighting, color-coded output, and sensible defaults make SnippetMind a joy to use.

### 📦 Packaging & Deployment

```bash
# Run tests
python -m pytest tests/ -v

# Build package
python setup.py sdist bdist_wheel

# Install locally
pip install -e .
```

### 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Commit Convention**: We follow the Angular commit convention:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test updates

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 简体中文

### 🎉 项目介绍

**SnippetMind-CLI** 是一款专为开发者打造的智能代码片段管理工具。与传统片段管理器不同，SnippetMind 利用 AI 功能（如自动语言检测、智能标签和语义搜索）让您的代码库真正智能化。

**灵感来源**：源于每天在散乱的代码文件、Stack Overflow 书签和混乱笔记中搜索的挫败感。SnippetMind 用一个强大的 CLI 工具将混乱变为有序。

**核心差异化亮点**：
- 🧠 **AI 自动分析**：自动检测编程语言、生成标签、建议描述
- 🔍 **语义搜索**：基于 SQLite FTS5 的全文搜索，智能排序
- ⚡ **零配置**：开箱即用，默认设置合理
- 🔒 **隐私优先**：所有数据存储在本地 SQLite 中——绝不上传

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🧠 **AI 语言检测** | 从代码模式自动检测 15+ 种编程语言 |
| 🏷️ **智能自动标签** | 通过内容分析自动分类代码片段 |
| 🔍 **全文搜索** | 基于 SQLite FTS5 的闪电般快速搜索 |
| 📋 **语法高亮** | 使用 Rich 终端渲染，代码展示美观 |
| ⭐ **收藏夹** | 标记并快速访问最常用的片段 |
| 📁 **集合管理** | 将片段组织到自定义集合中 |
| 📤 **导入/导出** | 支持 JSON 和 Markdown 格式 |
| 🎮 **交互模式** | TUI 风格的交互式片段管理 |
| 📊 **统计分析** | 洞察您的片段使用模式 |

**支持语言**：Python、JavaScript、TypeScript、Go、Rust、Java、C/C++、Bash、SQL、HTML、CSS、JSON、YAML、Dockerfile、Markdown 等！

### 🚀 快速开始

#### 环境要求
- Python 3.8 或更高版本
- pip 包管理器

#### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/SnippetMind-CLI.git
cd SnippetMind-CLI

# 安装依赖
pip install -r requirements.txt

# 安装为包（可选）
pip install -e .
```

#### 基本用法

```bash
# 添加新片段
snippetmind add --title "Hello World" --code "print('hello')" --language python

# 或使用短别名
sm add --title "API Request" --code "import requests" --tags "api,network"

# 搜索片段
sm search "hello"

# 列出所有片段
sm list

# 显示片段（带语法高亮）
sm show 1

# 复制片段到剪贴板
sm copy 1

# 切换收藏状态
sm favorite 1

# 查看统计
sm stats
```

### 📖 详细使用指南

#### 添加片段

```bash
# 命令行添加
sm add --title "Quick Sort" --code "def quicksort(arr):..." --language python

# 从剪贴板
sm add --title "From Clipboard" --from-clipboard

# 从文件
sm add --title "Config" --from-file ./config.py

# 完整元数据
sm add --title "Database Query" \
       --code "SELECT * FROM users" \
       --language sql \
       --description "Select all active users" \
       --tags "database,sql,users" \
       --source "https://docs.example.com"
```

#### 搜索

```bash
# 基础关键词搜索
sm search "function"

# 按语言过滤
sm search "api" --language python

# 语义搜索（基于关键词排序）
sm search "sort algorithm" --semantic
```

#### 管理集合

```bash
# 创建集合
sm collection create "Web Development" --description "Frontend and backend snippets"

# 列出集合
sm collection list

# 添加片段到集合
sm collection add 1 1
```

#### 交互模式

```bash
# 启动交互式 TUI
sm interactive
```

### 💡 设计思路

**本地优先架构**：所有片段存储在本地 SQLite 数据库（`~/.snippetmind/snippets.db`）。无需云依赖，无订阅费用，完全数据所有权。

**无云端 AI**：语言检测和标签生成完全在本地运行，使用模式匹配和启发式算法。无需 API 密钥，无速率限制，无隐私顾虑。

**开发者体验优先**：每个命令都设计得直观快速。语法高亮、彩色输出和合理的默认值让 SnippetMind 使用起来令人愉悦。

### 📦 打包与部署

```bash
# 运行测试
python -m pytest tests/ -v

# 构建包
python setup.py sdist bdist_wheel

# 本地安装
pip install -e .
```

### 🤝 贡献指南

欢迎贡献！请遵循以下规范：

1. Fork 本仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'feat: Add amazing feature'`）
4. 推送分支（`git push origin feature/amazing-feature`）
5. 创建 Pull Request

**提交规范**：遵循 Angular 提交约定：
- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试更新

### 📄 开源协议

本项目采用 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件。

---

## 繁體中文

### 🎉 專案介紹

**SnippetMind-CLI** 是一款專為開發者打造的智能程式碼片段管理工具。與傳統片段管理器不同，SnippetMind 利用 AI 功能（如自動語言檢測、智能標籤和語義搜尋）讓您的程式碼庫真正智能化。

**靈感來源**：源於每天在散亂的程式碼檔案、Stack Overflow 書籤和混亂筆記中搜尋的挫敗感。SnippetMind 用一個強大的 CLI 工具將混亂變為有序。

**核心差異化亮點**：
- 🧠 **AI 自動分析**：自動檢測程式語言、生成標籤、建議描述
- 🔍 **語義搜尋**：基於 SQLite FTS5 的全文搜尋，智能排序
- ⚡ **零配置**：開箱即用，預設設定合理
- 🔒 **隱私優先**：所有資料儲存在本地 SQLite 中——絕不上傳

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🧠 **AI 語言檢測** | 從程式碼模式自動檢測 15+ 種程式語言 |
| 🏷️ **智能自動標籤** | 透過內容分析自動分類程式碼片段 |
| 🔍 **全文搜尋** | 基於 SQLite FTS5 的閃電般快速搜尋 |
| 📋 **語法高亮** | 使用 Rich 終端渲染，程式碼展示美觀 |
| ⭐ **收藏夾** | 標記並快速存取最常用的片段 |
| 📁 **集合管理** | 將片段組織到自訂集合中 |
| 📤 **匯入/匯出** | 支援 JSON 和 Markdown 格式 |
| 🎮 **互動模式** | TUI 風格的互動式片段管理 |
| 📊 **統計分析** | 洞察您的片段使用模式 |

**支援語言**：Python、JavaScript、TypeScript、Go、Rust、Java、C/C++、Bash、SQL、HTML、CSS、JSON、YAML、Dockerfile、Markdown 等！

### 🚀 快速開始

#### 環境要求
- Python 3.8 或更高版本
- pip 套件管理器

#### 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/SnippetMind-CLI.git
cd SnippetMind-CLI

# 安裝依賴
pip install -r requirements.txt

# 安裝為套件（可選）
pip install -e .
```

#### 基本用法

```bash
# 新增片段
snippetmind add --title "Hello World" --code "print('hello')" --language python

# 或使用短別名
sm add --title "API Request" --code "import requests" --tags "api,network"

# 搜尋片段
sm search "hello"

# 列出所有片段
sm list

# 顯示片段（含語法高亮）
sm show 1

# 複製片段到剪貼簿
sm copy 1

# 切換收藏狀態
sm favorite 1

# 查看統計
sm stats
```

### 📖 詳細使用指南

#### 新增片段

```bash
# 命令列新增
sm add --title "Quick Sort" --code "def quicksort(arr):..." --language python

# 從剪貼簿
sm add --title "From Clipboard" --from-clipboard

# 從檔案
sm add --title "Config" --from-file ./config.py

# 完整元資料
sm add --title "Database Query" \
       --code "SELECT * FROM users" \
       --language sql \
       --description "Select all active users" \
       --tags "database,sql,users" \
       --source "https://docs.example.com"
```

#### 搜尋

```bash
# 基礎關鍵詞搜尋
sm search "function"

# 按語言過濾
sm search "api" --language python

# 語義搜尋（基於關鍵詞排序）
sm search "sort algorithm" --semantic
```

#### 管理集合

```bash
# 建立集合
sm collection create "Web Development" --description "Frontend and backend snippets"

# 列出集合
sm collection list

# 新增片段到集合
sm collection add 1 1
```

#### 互動模式

```bash
# 啟動互動式 TUI
sm interactive
```

### 💡 設計理念

**本地優先架構**：所有片段儲存在本地 SQLite 資料庫（`~/.snippetmind/snippets.db`）。無需雲端依賴，無訂閱費用，完全資料所有權。

**無雲端 AI**：語言檢測和標籤生成完全在本地執行，使用模式匹配和啟發式演算法。無需 API 金鑰，無速率限制，無隱私顧慮。

**開發者體驗優先**：每個命令都設計得直觀快速。語法高亮、彩色輸出和合理的預設值讓 SnippetMind 使用起來令人愉悅。

### 📦 打包與部署

```bash
# 執行測試
python -m pytest tests/ -v

# 建構套件
python setup.py sdist bdist_wheel

# 本地安裝
pip install -e .
```

### 🤝 貢獻指南

歡迎貢獻！請遵循以下規範：

1. Fork 本倉庫
2. 建立功能分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'feat: Add amazing feature'`）
4. 推送分支（`git push origin feature/amazing-feature`）
5. 建立 Pull Request

**提交規範**：遵循 Angular 提交約定：
- `feat:` 新功能
- `fix:` 修復問題
- `docs:` 文件更新
- `refactor:` 程式碼重構
- `test:` 測試更新

### 📄 開源協議

本專案採用 MIT 協議開源 - 詳見 [LICENSE](LICENSE) 檔案。

---

<div align="center">

Made with ❤️ by [gitstq](https://github.com/gitstq)

</div>
