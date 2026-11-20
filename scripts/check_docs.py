#!/usr/bin/env python3
"""文档一致性检查：相对链接是否有效，浏览器兜底说明是否两路都在。"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules"}
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")


def markdown_files():
    for path in ROOT.rglob("*.md"):
        if not any(part in SKIP_DIRS for part in path.parts):
            yield path


def check_links():
    problems = []
    for path in markdown_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in LINK_RE.finditer(text):
            target = match.group(1).split("#")[0]
            if not target or target.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            if not (path.parent / target).resolve().exists():
                problems.append(f"{path.relative_to(ROOT)} -> {target}")
    return problems


def check_hook_terms():
    """hook 是硬触发入口；正文已经拆成 ego/playwright 两路时，hook 不能只提一个。"""
    hook = ROOT / "examples" / "hook" / "research-trigger.py"
    text = hook.read_text(encoding="utf-8", errors="replace")
    missing = [name for name in ("ego-browser", "playwright-cli") if name not in text]
    if "web_fetch_exa" in text and missing:
        return [f"{hook.relative_to(ROOT)} 缺少浏览器兜底说明：{', '.join(missing)}"]
    return []


def check_readme_sync():
    """中英 README 的 H2 数量应当一致，防止只更新一边。"""
    def h2(path):
        text = path.read_text(encoding="utf-8", errors="replace")
        return len(re.findall(r"^## ", text, re.M))

    zh, en = ROOT / "README.md", ROOT / "README.en.md"
    if zh.exists() and en.exists() and h2(zh) != h2(en):
        return [f"README H2 数量不一致：中文 {h2(zh)} / 英文 {h2(en)}"]
    return []


def main():
    problems = check_links() + check_hook_terms() + check_readme_sync()
    if problems:
        print("发现 %d 个问题：" % len(problems))
        for item in problems:
            print("-", item)
        return 1
    print("文档检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())