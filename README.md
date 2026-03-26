# JSON to Obsidian

一个将JSON格式的AI聊天记录转换为Obsidian本地知识库Markdown格式的工具。

## 功能

- 将JSON文件转换为Obsidian兼容的Markdown格式
- 自动生成YAML frontmatter元数据
- 保留层级结构（## 章节、### 子项）
- 支持数组类型数据，每个对象生成独立文件
- 自动处理文件名（使用标题或UUID）

## 使用方法

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

## 输出格式

转换后的Markdown文件包含：

- **YAML Frontmatter**：创建时间、来源、关键字段
- **标题**：自动使用 `name` 字段或UUID
- **层级内容**：复杂对象拆分为章节结构

## 环境要求

- Python 3.6+
- 无需额外依赖
