import json
import os
import re
import sys
import urllib.request
from pathlib import Path

NOTION_VERSION = "2022-06-28"
API = "https://api.notion.com/v1"
MAX_BLOCKS = 100


def get_config():
    token = os.environ.get("NOTION_TOKEN", "").strip()
    parent = os.environ.get("NOTION_PARENT_PAGE_ID", "").strip()
    if not token or not parent:
        print("Error: set NOTION_TOKEN dan NOTION_PARENT_PAGE_ID")
        print("  PowerShell: $env:NOTION_TOKEN='...'; $env:NOTION_PARENT_PAGE_ID='...'")
        sys.exit(1)
    return token, parent


def notion_request(method, path, token, body=None):
    url = API + path
    headers = {
        "Authorization": "Bearer " + token,
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read().decode("utf-8"))
        sys.exit(1)


def text_block(content):
    return [{"type": "text", "text": {"content": content}}]


def block_for_line(line):
    if line.startswith("### "):
        return {"object": "block", "type": "heading_3",
                "heading_3": {"rich_text": text_block(line[4:])}}
    if line.startswith("## "):
        return {"object": "block", "type": "heading_2",
                "heading_2": {"rich_text": text_block(line[3:])}}
    if line.startswith("# "):
        return {"object": "block", "type": "heading_1",
                "heading_1": {"rich_text": text_block(line[2:])}}
    if line.startswith("> "):
        return {"object": "block", "type": "quote",
                "quote": {"rich_text": text_block(line[2:])}}
    if line.startswith("---"):
        return {"object": "block", "type": "divider", "divider": {}}
    if line.startswith("- "):
        return {"object": "block", "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": text_block(line[2:])}}
    return None


def parse_table(lines, token):
    def strip_cell(cell):
        return re.sub(r"[`*_]", "", cell.strip())

    header = [strip_cell(c) for c in lines[0].split("|")[1:-1]]
    rows = []
    for raw in lines[2:]:
        if raw.strip().startswith("|"):
            cells = [strip_cell(c) for c in raw.split("|")[1:-1]]
            if cells:
                rows.append(cells)
    width = len(header)
    if width == 0:
        return None
    children = []
    for r in [header] + rows:
        row_cells = []
        for i in range(width):
            val = r[i] if i < len(r) else ""
            row_cells.append([{"type": "text", "text": {"content": val}}])
        children.append({"type": "table_row",
                         "table_row": {"cells": row_cells}})
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": width,
            "has_column_header": True,
            "has_row_header": False,
            "children": children,
        },
    }


LANG_MAP = {
    "text": "plain text",
    "txt": "plain text",
    "json": "json",
    "bash": "bash",
    "sh": "bash",
    "shell": "shell",
    "python": "python",
    "py": "python",
    "js": "javascript",
    "javascript": "javascript",
    "sql": "sql",
    "yaml": "yaml",
    "yml": "yaml",
}


def code_block(lang, lines):
    lang = LANG_MAP.get((lang or "").strip().lower(), "plain text")
    return {
        "object": "block",
        "type": "code",
        "code": {
            "language": lang,
            "rich_text": text_block("\n".join(lines)),
        },
    }


def md_to_blocks(text):
    blocks = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()

        if stripped.strip().startswith("```"):
            lang = stripped.strip()[3:].strip()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append(code_block(lang, code_lines))
            i += 1
            continue

        if stripped.startswith("|"):
            j = i
            table_lines = []
            while j < len(lines) and lines[j].strip().startswith("|"):
                table_lines.append(lines[j])
                j += 1
            if len(table_lines) >= 3:
                blocks.append(parse_table(table_lines, None))
                i = j
                continue

        if stripped.strip() == "":
            i += 1
            continue

        blk = block_for_line(stripped)
        if blk:
            blocks.append(blk)
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": text_block(stripped)},
            })
        i += 1
    return blocks


def append_blocks(token, block_id, blocks):
    for start in range(0, len(blocks), MAX_BLOCKS):
        chunk = blocks[start:start + MAX_BLOCKS]
        notion_request("PATCH", f"/blocks/{block_id}/children", token,
                       {"children": chunk})


def create_page(token, parent_id, title, blocks):
    page = notion_request("POST", "/pages", token, {
        "parent": {"page_id": parent_id},
        "properties": {"title": {"title": [{"text": {"content": title}}]}},
    })
    page_id = page["id"]
    append_blocks(token, page_id, blocks)
    return page["url"]


def main():
    token, parent_id = get_config()
    root = Path(__file__).resolve().parent.parent
    docs = {
        "Rencana Proyek": root / "Rencana-Proyek.md",
        "Kebutuhan Data": root / "Kebutuhan-Data.md",
    }
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for title, path in docs.items():
        if only and only not in title:
            continue
        if not path.exists():
            print(f"File tidak ditemukan: {path}")
            continue
        blocks = md_to_blocks(path.read_text(encoding="utf-8"))
        url = create_page(token, parent_id, title, blocks)
        print(f"OK  {title} -> {url}")


if __name__ == "__main__":
    main()