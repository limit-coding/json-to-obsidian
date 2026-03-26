# Obsidian Data Converters

将各种 AI 聊天记录转换为 Obsidian 本地知识库 Markdown 格式的工具集。

## 工具列表

| 工具 | 功能 | 输入格式 |
|------|------|----------|
| `json_to_obsidian.py` | JSON 转 Markdown | JSON |
| `gemini_html_to_md.py` | Gemini HTML 转 Markdown | Google Takeout HTML |
| `obsidian_indexer.py` | 生成 Obsidian 知识库索引 | Markdown 文件夹 |

---

## json_to_obsidian.py

将 JSON 格式的 AI 聊天记录转换为 Obsidian 兼容的 Markdown 格式。

### 功能

- 将 JSON 文件转换为 Obsidian 兼容的 Markdown 格式
- 自动生成 YAML frontmatter 元数据
- 保留层级结构（## 章节、### 子项）
- 支持数组类型数据，每个对象生成独立文件
- 自动处理文件名（使用标题或 UUID）

### 使用方法

```bash
python3 json_to_obsidian.py <json文件> [输出目录]
```

### 示例

```bash
# 转换单个文件
python3 json_to_obsidian.py conversations.json

# 指定输出目录
python3 json_to_obsidian.py conversations.json ./my_obsidian_notes
```

---

## gemini_html_to_md.py

将 Google Takeout 导出的 Gemini Apps 活动记录 HTML 转换为 Obsidian Markdown 格式。

### 功能

- 解析 Google Takeout HTML 格式的 Gemini 活动记录
- 自动提取 Prompt、回复内容、时间戳
- 生成 Obsidian 兼容的 Markdown 文件
- 自动创建日期索引文件
- 支持 YAML frontmatter 便于知识库检索

### 使用方法

```bash
python3 gemini_html_to_md.py
```

默认配置：
- 输入：`~/Desktop/Takeout/我的活动/Gemini Apps/我的活动记录.html`
- 输出：`~/Desktop/Takeout/Gemini_Conversations/`

### 修改输入输出路径

编辑脚本末尾的参数：

```python
if __name__ == "__main__":
    html_file = "你的HTML文件路径"
    output_dir = "你的输出目录路径"
    process_gemini_html(html_file, output_dir)
```

### 输出格式

```
Gemini_Conversations/
├── 000_INDEX.md              # 总索引
├── 2025-05-17.md             # 每日索引
├── 2025-05-17_001_xxx.md     # 具体对话
└── 2025-05-17_002_xxx.md
```

每个对话文件包含：
- YAML frontmatter（创建时间、日期、来源）
- Prompt（用户提问）
- Response（Gemini 回复）

### 环境要求

- Python 3.6+
- 无需额外依赖（使用内置 `re` 模块）

---

## obsidian_indexer.py

为 Obsidian 知识库生成双向链接索引，支持时间线、主题标签、同日期关联等功能。

### 功能

- 扫描所有对话 Markdown 文件
- 生成 MOC (Map of Content) 总览索引
- 按月份生成月度索引
- 按主题/关键词生成标签索引
- 自动生成反向链接（相关对话推荐）
- 支持 Obsidian `[[双链]]` 语法

### 使用方法

```bash
python3 obsidian_indexer.py
```

默认配置：
- 源目录：`~/Desktop/Takeout/Gemini_Conversations`
- 输出：`源目录/99_Index/`

### 输出结构

```
99_Index/
├── MOC.md              # 知识库总览
├── Tags.md             # 主题标签索引
├── Today.md            # 今日对话
├── YYYY-MM.md          # 月度索引（如 2026-03.md）
└── Backlinks/          # 反向链接
    └── *.md            # 每个对话的相关对话
```

### 主题分类

自动识别以下主题：
- 学习、编程、AI、科研、实习、UAV/无人机、课程、竞赛

### 环境要求

- Python 3.6+
- 无需额外依赖

---

## 环境要求

- Python 3.6+
- 无需额外依赖（所有工具使用 Python 内置模块）
