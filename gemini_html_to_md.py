#!/usr/bin/env python3
"""
Gemini HTML Activity to Obsidian Markdown converter
Using regex extraction for reliability
"""

import os
import re
from pathlib import Path
from datetime import datetime

def extract_conversations(html_path):
    """Extract conversations using regex"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match outer-cell containing Gemini Apps
    # Each cell has: header (Gemini Apps), content (prompt + response + datetime)
    pattern = r'<div class="outer-cell[^"]*">.*?<div class="header-cell[^"]*">.*?Gemini Apps.*?</div>.*?<div class="content-cell[^"]*mdl-typography--body-1[^"]*">(.+?)</div>.*?<div class="content-cell[^"]*mdl-typography--text-right'

    matches = re.findall(pattern, content, re.DOTALL)
    print(f"Found {len(matches)} potential conversation blocks")

    conversations = []
    for match in matches:
        # Extract datetime: "2026年3月26日 13:08:19 HKT"
        dt_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日 (\d{2}:\d{2}:\d{2})', match)
        if not dt_match:
            continue

        y, mo, d, t = dt_match.groups()
        date_str = f"{y}-{int(mo):02d}-{int(d):02d}"
        datetime_str = f"{date_str} {t}"

        # Remove HTML tags for text extraction
        text = re.sub(r'<[^>]+>', ' ', match)
        text = re.sub(r'\s+', ' ', text).strip()

        # Split by datetime to get prompt and response
        parts = re.split(r'\d{4}年\d{1,2}月\d{1,2}日 \d{2}:\d{2}:\d{2}', text, maxsplit=1)

        if len(parts) >= 2:
            prompt_match = re.search(r'Prompted\s+(.+)', parts[0])
            prompt = prompt_match.group(1).strip() if prompt_match else parts[0].replace('Prompted', '').strip()
            response = parts[1].strip()
        else:
            continue

        # Skip if prompt is too short
        if len(prompt) < 3:
            continue

        conversations.append({
            'date': date_str,
            'datetime': datetime_str,
            'prompt': prompt,
            'response': response
        })

    return conversations

def clean_text(text):
    """Clean extracted text"""
    text = re.sub(r'\s*20\d{2}年\d{1,2}月\d{1,2}日 \d{2}:\d{2}:\d{2} HKT\s*', '', text)
    text = re.sub(r'^\s*Prompted\s*', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def convert_to_markdown(conv, index):
    """Convert conversation to Obsidian Markdown"""
    prompt = conv['prompt'][:100] if len(conv['prompt']) > 100 else conv['prompt']

    lines = [
        "---",
        f"created: {conv['datetime']}",
        f"date: {conv['date']}",
        "source: Gemini Apps (Google Takeout)",
        "type: gemini-conversation",
        "---",
        "",
        f"# {prompt}",
        "",
        f"> **Prompt:** {conv['prompt']}",
        "",
        "## Response",
        "",
        clean_text(conv['response']),
        ""
    ]

    return '\n'.join(lines)

def process_gemini_html(input_path, output_dir):
    """Process Gemini HTML file"""
    print(f"Parsing {input_path}...")

    conversations = extract_conversations(input_path)
    print(f"Extracted {len(conversations)} conversations")

    if not conversations:
        print("No conversations found!")
        return

    # Sort by datetime
    conversations.sort(key=lambda x: x['datetime'])

    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Group by date
    by_date = {}
    for conv in conversations:
        date = conv['date']
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(conv)

    # Create files
    for i, conv in enumerate(conversations):
        md = convert_to_markdown(conv, i)

        safe_prompt = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', conv['prompt'])[:40]
        safe_prompt = re.sub(r'\s+', '_', safe_prompt.strip())
        safe_prompt = re.sub(r'_+', '_', safe_prompt)

        filename = f"{conv['date']}_{i+1:03d}_{safe_prompt}.md"

        with open(output_dir / filename, 'w', encoding='utf-8') as f:
            f.write(md)

        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(conversations)}...")

    print(f"  Processed {len(conversations)}/{len(conversations)}...")

    # Create index
    index_lines = [
        "---",
        f"created: {datetime.now().isoformat()}",
        "source: Gemini Apps",
        "type: index",
        "---",
        "",
        "# Gemini Conversations Index",
        "",
        f"Total: {len(conversations)} conversations",
        f"Range: {conversations[0]['date']} to {conversations[-1]['date']}",
        "",
        "## By Date",
        ""
    ]

    for date, convs in by_date.items():
        index_lines.append(f"- [[{date}|{date}]] ({len(convs)} conversations)")

    with open(output_dir / "000_INDEX.md", 'w', encoding='utf-8') as f:
        f.write('\n'.join(index_lines))

    # Create per-date files
    for date, convs in by_date.items():
        date_lines = [
            "---",
            f"created: {datetime.now().isoformat()}",
            f"date: {date}",
            "source: Gemini Apps",
            "type: daily-index",
            "---",
            "",
            f"# {date}",
            "",
            f"## Conversations ({len(convs)})",
            ""
        ]
        for j, conv in enumerate(convs):
            title = conv['prompt'][:60]
            safe = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', conv['prompt'])[:30]
            safe = re.sub(r'\s+', '_', safe.strip())
            date_lines.append(f"- [[{date}_{j+1:03d}_{safe}|{title}]]")
        with open(output_dir / f"{date}.md", 'w', encoding='utf-8') as f:
            f.write('\n'.join(date_lines))

    print(f"\nDone! Created {len(conversations)} files in {output_dir}")

if __name__ == "__main__":
    html_file = "/Users/limit/Desktop/Takeout/我的活动/Gemini Apps/我的活动记录.html"
    output_dir = "/Users/limit/Desktop/Takeout/Gemini_Conversations"

    process_gemini_html(html_file, output_dir)
