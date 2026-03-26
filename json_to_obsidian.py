#!/usr/bin/env python3
"""
JSON to Obsidian Markdown converter
Converts JSON files to Markdown format with YAML frontmatter for Obsidian
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

def json_to_markdown_value(value, indent=0):
    """Convert a JSON value to markdown formatted string"""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        # Escape Obsidian special chars and wrap in quotes if contains special chars
        if any(c in value for c in [':', '#', '|', '\n', '[', ']']) or value.startswith(' ') or value.endswith(' '):
            return f'"{value}"'
        return value
    elif isinstance(value, list):
        if not value:
            return "[]"
        items = []
        for item in value:
            item_str = json_to_markdown_value(item, indent + 1)
            items.append(f"- {item_str}")
        return "\n".join(items)
    elif isinstance(value, dict):
        if not value:
            return "{}"
        items = []
        for k, v in value.items():
            v_str = json_to_markdown_value(v, indent + 1)
            items.append(f"{k}: {v_str}")
        return "\n".join(items)
    return str(value)

def convert_json_to_md(json_data, title=None):
    """Convert JSON object to Obsidian markdown with frontmatter"""
    lines = []

    # YAML frontmatter
    lines.append("---")
    lines.append(f"created: {datetime.now().isoformat()}")
    lines.append(f"source: json")

    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if key in ('created_at', 'updated_at'):
                lines.append(f"{key}: {value}")
            elif isinstance(value, (str, int, float, bool)):
                # Sanitize YAML value
                val_str = str(value).replace('"', '\\"')
                if ':' in val_str or '#' in val_str or '\n' in val_str:
                    lines.append(f'{key}: "{val_str}"')
                else:
                    lines.append(f"{key}: {val_str}")
            elif isinstance(value, list) and len(value) <= 5 and all(isinstance(x, (str, int, float, bool)) for x in value):
                lines.append(f"{key}: [{', '.join(str(x) for x in value)}]")
            # Skip complex nested structures from frontmatter

    lines.append("---")
    lines.append("")

    # Title
    if title:
        lines.append(f"# {title}")
        lines.append("")
    elif isinstance(json_data, dict) and 'name' in json_data:
        lines.append(f"# {json_data['name']}")
        lines.append("")
    elif isinstance(json_data, dict) and 'uuid' in json_data:
        lines.append(f"# {json_data['uuid']}")
        lines.append("")

    # Content
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if key in ('created_at', 'updated_at', 'uuid', 'name'):
                continue
            if isinstance(value, (dict, list)) and value:
                lines.append(f"## {key}")
                lines.append("")
                if isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            lines.append(f"### Item {i+1}")
                            for k, v in item.items():
                                lines.append(f"- **{k}**: {json_to_markdown_value(v)}")
                            lines.append("")
                        else:
                            lines.append(f"- {json_to_markdown_value(item)}")
                else:
                    for k, v in value.items():
                        lines.append(f"- **{k}**: {json_to_markdown_value(v)}")
                lines.append("")
            elif value:
                lines.append(f"## {key}")
                lines.append("")
                lines.append(json_to_markdown_value(value))
                lines.append("")

    return "\n".join(lines)

def process_file(input_path, output_dir=None):
    """Process a single JSON file and convert to markdown"""
    input_path = Path(input_path)

    if output_dir is None:
        output_dir = input_path.parent / f"{input_path.stem}_obsidian"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(exist_ok=True)

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, list):
        # Array of objects - create one file per object
        for i, item in enumerate(data):
            title = None
            if 'name' in item and item['name']:
                title = item['name']
            elif 'uuid' in item:
                title = item['uuid']

            md_content = convert_json_to_md(item, title=title)
            filename = f"{input_path.stem}_{i+1}"
            if title and isinstance(title, str) and title.strip():
                # Sanitize title for filename
                safe_title = "".join(c if c.isalnum() or c in ' -_' else '_' for c in title[:50])
                filename = safe_title

            output_path = output_dir / f"{filename}.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"Created: {output_path}")
    else:
        # Single object
        md_content = convert_json_to_md(data)
        output_path = output_dir / f"{input_path.stem}.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"Created: {output_path}")

    return output_dir

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python json_to_obsidian.py <json_file> [output_dir]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    process_file(input_file, output_dir)
