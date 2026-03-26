#!/usr/bin/env python3
"""
Obsidian Knowledge Base Indexer
为 Obsidian 知识库生成双向链接索引
"""

import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set

class ObsidianIndexer:
    def __init__(self, source_dir: str, output_dir: str = None):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir) if output_dir else self.source_dir
        self.conversations = []
        self.tag_index = defaultdict(list)  # tag -> [(date, filename, prompt)]
        self.keyword_index = defaultdict(list)  # keyword -> [(date, filename, prompt)]
        self.date_index = defaultdict(list)  # date -> [filename]

        # 常见关键词模式
        self.keyword_patterns = {
            '学习': ['学习', '课程', '教材', '上课', '复习', '考试', '笔记'],
            '编程': ['代码', 'Python', '编程', '算法', '程序', '函数', 'bug', 'debug'],
            'AI': ['AI', 'Gemini', '模型', '训练', 'LLM', 'ChatGPT', 'prompt'],
            'AI前沿': ['GPT', 'Claude', 'Llama', 'AGI', 'Sora', 'GPT-5', 'o1', 'o3', '推理模型', '多模态', '大模型', 'Grok', 'Mistral', 'Gemini模型'],
            '科研': ['论文', '研究', '实验', '课题', '导师', '实验室', 'SCI', '顶会'],
            '实习': ['实习', '面试', 'Offer', '简历', '秋招', '春招', '字节', '腾讯', '阿里'],
            'UAV/无人机': ['无人机', 'UAV', '视觉', '飞控', '避障', '航拍', '四旋翼'],
            '课程': ['模电', '数电', '信号', '通信', '电磁', '概率', '线代', '高数'],
            '竞赛': ['竞赛', '比赛', '数学建模', 'ACM', '电赛', 'robomaster'],
            'CS公开课': ['cs61a', 'csapp', 'mit公开课', '翁恺', 'b站课程', '自学编程', 'leetcode', '刷题', '公开课', 'CS61A', 'CSAPP'],
            '情感/恋爱': ['女朋友', '男朋友', '喜欢', '暗恋', '表白', '恋爱', '分手', '复合', '追', '约会', '对象'],
            '心理/情绪': ['压力', '焦虑', '迷茫', '困惑', '心情', '抑郁', '孤独', '难受', '痛苦', '心理', '情绪'],
            '人际关系': ['室友', '宿舍', '社交', '人际', '朋友', '同学', '班级', '关系', '矛盾', '孤立', '合群'],
            '生活日常': ['生活', '日常', '吃饭', '作息', '睡眠', '习惯', '运动', '健身', '减肥', '娱乐', '放假', '周末'],
            '历史/思想': ['历史', '古代', '朝代', '皇帝', '战争', '革命', '马克思', '毛泽东', '哲学', '意识形态', '资本主义', '社会主义', '共产主义', '政治', '民主', '专制', '改革', '变革'],
        }

    def scan_conversations(self):
        """扫描所有对话文件"""
        for md_file in self.source_dir.glob("*.md"):
            if md_file.name.startswith("000_"):
                continue

            content = md_file.read_text(encoding='utf-8')
            frontmatter = self._parse_frontmatter(content)

            # 提取日期和标题
            date = frontmatter.get('date', 'unknown')
            created = frontmatter.get('created', '')
            prompt = frontmatter.get('prompt', '')

            if not prompt:
                # 从文件名提取
                match = re.search(r'\d{4}-\d{2}-\d{2}_\d{3}_(.+)\.md', md_file.name)
                if match:
                    prompt = match.group(1).replace('_', ' ')

            self.conversations.append({
                'filename': md_file.stem,  # 无扩展名
                'date': date,
                'created': created,
                'prompt': prompt,
                'path': md_file
            })

            # 索引到日期
            if date != 'unknown':
                self.date_index[date].append(md_file.stem)

            # 索引到关键词
            self._index_keywords(date, md_file.stem, prompt)

        print(f"扫描到 {len(self.conversations)} 个对话文件")

    def _parse_frontmatter(self, content: str) -> Dict:
        """解析 YAML frontmatter"""
        frontmatter = {}
        if content.startswith('---'):
            parts = content[3:].split('---', 1)
            if len(parts) > 1:
                for line in parts[0].strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip().strip('"')
        return frontmatter

    def _index_keywords(self, date: str, filename: str, prompt: str):
        """根据 prompt 内容建立关键词索引"""
        for category, keywords in self.keyword_patterns.items():
            for kw in keywords:
                if kw.lower() in prompt.lower():
                    self.tag_index[category].append((date, filename, prompt))
                    break

    def generate_moc(self) -> str:
        """生成主索引 (Map of Content)"""
        lines = [
            "---",
            f"created: {datetime.now().isoformat()}",
            "type: MOC",
            "tags: [MOC]",
            "---",
            "",
            "# Gemini 知识库总览",
            "",
            f"> 📊 共 {len(self.conversations)} 条对话记录",
            "",
            "---",
            "",
            "## 📅 时间线索引",
            "",
            "### 按月份",
            ""
        ]

        # 按月份分组
        monthly = defaultdict(list)
        for conv in self.conversations:
            if conv['date'] != 'unknown':
                month = conv['date'][:7]  # YYYY-MM
                monthly[month].append(conv)

        for month in sorted(monthly.keys(), reverse=True):
            lines.append(f"#### {month}")
            lines.append(f"- [[{month}|{month} 月]] ({len(monthly[month])} 条)")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## 🏷️ 主题索引",
            ""
        ])

        for category in sorted(self.tag_index.keys()):
            items = self.tag_index[category]
            lines.append(f"### {category} ({len(items)} 条)")
            # 只显示前5条
            for date, filename, prompt in items[:5]:
                short_prompt = prompt[:40] + "..." if len(prompt) > 40 else prompt
                lines.append(f"- [[{filename}|{short_prompt}]]")
            if len(items) > 5:
                lines.append(f"- ... 还有 {len(items) - 5} 条")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## 📆 最近对话",
            ""
        ])

        # 最近20条
        sorted_convs = sorted(self.conversations, key=lambda x: x['date'], reverse=True)
        for conv in sorted_convs[:20]:
            short_prompt = conv['prompt'][:50] + "..." if len(conv['prompt']) > 50 else conv['prompt']
            lines.append(f"- [[{conv['filename']}|{conv['date']} {short_prompt}]]")

        return '\n'.join(lines)

    def generate_monthly_index(self, year_month: str, conversations: List) -> str:
        """生成月度索引"""
        lines = [
            "---",
            f"created: {datetime.now().isoformat()}",
            f"date: {year_month}",
            "type: monthly-index",
            "tags: [monthly]",
            "---",
            "",
            f"# {year_month} 对话记录",
            "",
            f"> 📊 {year_month} 月共 {len(conversations)} 条对话",
            "",
            "---",
            "",
            "## 全部对话",
            ""
        ]

        for conv in sorted(conversations, key=lambda x: x['created'], reverse=True):
            short_prompt = conv['prompt'][:60] + "..." if len(conv['prompt']) > 60 else conv['prompt']
            lines.append(f"- [[{conv['filename']}|{conv['date']} - {short_prompt}]]")

        return '\n'.join(lines)

    def generate_tags_index(self) -> str:
        """生成标签索引"""
        lines = [
            "---",
            f"created: {datetime.now().isoformat()}",
            "type: tags-index",
            "tags: [tags]",
            "---",
            "",
            "# 主题标签索引",
            "",
            "---",
            ""
        ]

        for category in sorted(self.tag_index.keys()):
            items = self.tag_index[category]
            lines.append(f"## {category}")
            lines.append("")
            lines.append(f"共 {len(items)} 条记录")
            lines.append("")

            for date, filename, prompt in sorted(items, key=lambda x: x[0], reverse=True):
                short_prompt = prompt[:60] + "..." if len(prompt) > 60 else prompt
                lines.append(f"- [[{filename}|{date} - {short_prompt}]]")

            lines.append("")

        return '\n'.join(lines)

    def generate_today_index(self) -> str:
        """生成今日索引（如果当天有对话）"""
        today = datetime.now().strftime('%Y-%m-%d')

        if today not in self.date_index:
            return None

        today_convs = [c for c in self.conversations if c['date'] == today]

        lines = [
            "---",
            f"created: {datetime.now().isoformat()}",
            f"date: {today}",
            "type: daily",
            "tags: [daily]",
            "---",
            "",
            f"# 📅 今日对话 - {today}",
            "",
            f"> 今天有 {len(today_convs)} 条新对话",
            "",
            "---",
            "",
        ]

        for conv in today_convs:
            short_prompt = conv['prompt']
            lines.append(f"## [[{conv['filename']}|{short_prompt}]]")

        return '\n'.join(lines)

    def generate_backlinks(self, filename: str, conversations: List) -> str:
        """为单个文件生成反向链接索引"""
        # 查找相关对话
        related = []
        for conv in conversations:
            if conv['filename'] == filename:
                related.append(conv)
                break

        if not related:
            return None

        conv = related[0]

        lines = [
            "---",
            f"created: {conv['created']}",
            f"date: {conv['date']}",
            "type: backlinks",
            "tags: [backlinks]",
            "---",
            "",
            f"# {conv['prompt']}",
            "",
            f"> 📅 {conv['date']} | 🔗 此对话的反向链接",
            "",
            "---",
            "",
            "## 关联对话",
            ""
        ]

        # 查找同日期的对话
        same_date = [c for c in conversations if c['date'] == conv['date'] and c['filename'] != filename]
        if same_date:
            lines.append("### 同日期")
            for c in same_date[:5]:
                short = c['prompt'][:50] + "..." if len(c['prompt']) > 50 else c['prompt']
                lines.append(f"- [[{c['filename']}|{short}]]")

        # 查找包含相同关键词的对话
        for category, keywords in self.keyword_patterns.items():
            for kw in keywords:
                if kw.lower() in conv['prompt'].lower():
                    same_topic = [c for c in conversations
                                  if c['filename'] != filename
                                  and kw.lower() in c['prompt'].lower()]
                    if same_topic:
                        lines.append(f"### 相关主题: {category}")
                        for c in same_topic[:5]:
                            short = c['prompt'][:50] + "..." if len(c['prompt']) > 50 else c['prompt']
                            lines.append(f"- [[{c['filename']}|{short}]]")
                    break

        return '\n'.join(lines)

    def build(self):
        """构建所有索引文件"""
        self.scan_conversations()

        # 创建索引目录
        index_dir = self.output_dir / "99_Index"
        index_dir.mkdir(exist_ok=True)

        # 1. 主索引 (MOC)
        moc_content = self.generate_moc()
        (index_dir / "MOC.md").write_text(moc_content, encoding='utf-8')
        print(f"✓ 生成 MOC.md")

        # 2. 月度索引
        monthly = defaultdict(list)
        for conv in self.conversations:
            if conv['date'] != 'unknown':
                month = conv['date'][:7]
                monthly[month].append(conv)

        for month, convs in monthly.items():
            content = self.generate_monthly_index(month, convs)
            (index_dir / f"{month}.md").write_text(content, encoding='utf-8')
        print(f"✓ 生成 {len(monthly)} 个月度索引")

        # 3. 标签索引
        tags_content = self.generate_tags_index()
        (index_dir / "Tags.md").write_text(tags_content, encoding='utf-8')
        print(f"✓ 生成 Tags.md")

        # 4. 今日索引
        today_content = self.generate_today_index()
        if today_content:
            (index_dir / "Today.md").write_text(today_content, encoding='utf-8')
            print(f"✓ 生成 Today.md")

        # 5. 为每个对话文件创建反向链接
        backlinks_dir = index_dir / "Backlinks"
        backlinks_dir.mkdir(exist_ok=True)

        for conv in self.conversations:
            content = self.generate_backlinks(conv['filename'], self.conversations)
            if content:
                (backlinks_dir / f"{conv['filename']}.md").write_text(content, encoding='utf-8')

        print(f"✓ 生成 {len(self.conversations)} 个反向链接文件")

        # 6. 更新主仓库的 README（如果需要）
        readme_content = self._generate_readme()
        (self.output_dir / "README.md").write_text(readme_content, encoding='utf-8')
        print(f"✓ 更新 README.md")

        print(f"\n✅ 索引构建完成！")
        print(f"   输出目录: {index_dir}")
        print(f"   - MOC.md (总览)")
        print(f"   - Tags.md (主题索引)")
        print(f"   - Today.md (今日)")
        print(f"   - YYYY-MM.md (月度索引)")
        print(f"   - Backlinks/*.md (反向链接)")

    def _generate_readme(self) -> str:
        """生成仓库 README"""
        return f"""# Obsidian Gemini 知识库

本仓库包含从 Google Takeout 导出的 Gemini 对话记录，已转换为 Obsidian Markdown 格式。

## 文件结构

```
Gemini_Conversations/
├── *.md                    # 对话文件
├── 99_Index/              # 知识库索引
│   ├── MOC.md            # 总览索引
│   ├── Tags.md           # 主题标签索引
│   ├── Today.md          # 今日对话
│   ├── YYYY-MM.md        # 月度索引
│   └── Backlinks/        # 反向链接
│       └── *.md
```

## Obsidian 使用指南

### 1. 克隆本仓库到 Obsidian Vault

```bash
git clone https://github.com/limit-coding/json-to-obsidian.git <你的Vault路径>
```

### 2. 索引功能说明

- **MOC.md** - 知识库总览，包含时间线和主题索引
- **Tags.md** - 按主题分类的所有对话
- **YYYY-MM.md** - 月度对话索引
- **Backlinks/** - 每个对话的相关对话推荐

### 3. 双向链接

Obsidian 支持 `[[文件名]]` 语法进行双向链接。点击任意链接可跳转到对应对话。

## 自动更新

使用 `gemini_html_to_md.py` 从 Google Takeout 导出新的 HTML 后，再运行 `obsidian_indexer.py` 更新索引：

```bash
python3 gemini_html_to_md.py
python3 obsidian_indexer.py
```

## 工具说明

| 工具 | 功能 |
|------|------|
| `gemini_html_to_md.py` | HTML 转 Markdown |
| `obsidian_indexer.py` | 生成 Obsidian 索引 |

---
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""


if __name__ == "__main__":
    # 默认配置
    source_dir = "/Users/limit/Desktop/Takeout/Gemini_Conversations"
    output_dir = "/Users/limit/Desktop/Takeout/Gemini_Conversations"

    indexer = ObsidianIndexer(source_dir, output_dir)
    indexer.build()
