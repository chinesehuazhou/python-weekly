#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将周刊全文发布到爱发电（ifdian.net），保存为草稿。

通过 CDP 连接已运行的 Edge 浏览器，自动填入标题、正文、选择方案并保存。

用法:
    .venv/bin/python resources/ifdian_publish.py docs/YYYY-MM-DD-weekly.md
"""

import sys
import json
import time
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

CDP_URL = "http://localhost:18800"
IFDIAN_EDITOR = "https://ifdian.net/edit/article"
PLAN_NAME = "￥128.00 /年 - 小月亮"
TITLE_PREFIX = "Python 潮流周刊"


def strip_frontmatter(md_text: str) -> str:
    """去掉 YAML frontmatter。"""
    lines = md_text.split("\n")
    if not lines or lines[0].strip() != "---":
        return md_text
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return md_text
    return "\n".join(lines[end_idx + 1:])


def find_or_create_ifdian_page(context):
    """在已有页签中查找爱发电页面，没有则新建页签。"""
    for page in context.pages:
        if "ifdian.net" in (page.url or "").lower():
            print(f"🔗 找到爱发电已有页签: {page.url}")
            return page

    page = context.new_page()
    print("🔗 新建页签用于爱发电发布")
    return page


def main():
    if len(sys.argv) < 2:
        print("用法: python ifdian_publish.py <weekly_md_path>")
        sys.exit(1)

    md_path = sys.argv[1]
    if not Path(md_path).exists():
        print(f"❌ 文件不存在: {md_path}")
        sys.exit(1)

    with open(md_path, "r", encoding="utf-8") as f:
        raw = f.read()

    # 提取标题：优先从 frontmatter，其次从 body 中的 H1
    title = ""
    frontmatter_match = re.search(r'^title:\s*"([^"]*)"', raw, re.MULTILINE)
    if frontmatter_match:
        title = frontmatter_match.group(1).strip()
    elif frontmatter_match := re.search(r"^title:\s*'([^']*)'", raw, re.MULTILINE):
        title = frontmatter_match.group(1).strip()

    body = strip_frontmatter(raw)
    body_lines = body.split("\n")
    body_without_h1_lines = []
    found_h1 = False
    for line in body_lines:
        if not found_h1 and line.strip().startswith("# ") and not line.strip().startswith("## "):
            if not title:
                title = line.strip().replace("# ", "").strip()
            found_h1 = True
            continue
        body_without_h1_lines.append(line)
    body_without_h1 = "\n".join(body_without_h1_lines).strip()

    if not title:
        print("❌ 未找到标题")
        sys.exit(1)

    # 去掉末尾的微信关注行
    body_without_h1 = re.sub(
        r'\n\*\*微信关注 Python猫\*\*[：:]\s*\[?https?://[^\n]+\]?\(https?://[^\n]+\)\s*$',
        '', body_without_h1
    )

    print(f"📝 标题: {title}")

    # pandoc 转换 Markdown → HTML
    import subprocess
    result = subprocess.run([
        "pandoc", "-f", "markdown", "-t", "html5",
        "--no-highlight", "--wrap=none", "--quiet", "-",
    ], input=body_without_h1, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ pandoc 转换失败: {result.stderr}")
        sys.exit(1)

    html = result.stdout
    html = re.sub(r'<h2 id="[^"]*">', '<h2>', html)
    html = html.strip()
    print(f"📏 HTML 长度: {len(html)} 字符")

    with sync_playwright() as p:
        print("🔗 通过 CDP 连接已有 Edge...")
        browser = p.chromium.connect_over_cdp(CDP_URL)

        if not browser.contexts:
            print("❌ 没有打开的浏览器上下文")
            sys.exit(1)

        context = browser.contexts[0]
        page = find_or_create_ifdian_page(context)

        # 导航到编辑器
        print("🌐 导航到爱发电编辑器...")
        page.goto(IFDIAN_EDITOR, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)

        # 检查登录
        if "login" in page.url.lower():
            print("⚠️ 需要登录爱发电！请先在 Edge 中登录后按 Enter...")
            input()
            page.goto(IFDIAN_EDITOR, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)

        try:
            # 1. 填入标题
            print("\n1. 填入标题...")
            try:
                title_input = page.locator('input[placeholder*="标题"]').first
                title_input.click()
                page.wait_for_timeout(300)
                title_input.fill("")
                title_input.fill(title)
                page.wait_for_timeout(500)
                print(f"  ✓ 标题已填: {title[:50]}")
            except Exception as e:
                print(f"  ⚠ 填入标题失败: {e}")

            # 2. 填入正文（Froala 编辑器，contenteditable）
            print("2. 填入正文...")
            try:
                escaped_html = json.dumps(html)
                result = page.evaluate(f"""
                    (function() {{
                        const editor = document.querySelector('[contenteditable]');
                        if (editor) {{
                            editor.focus();
                            editor.innerHTML = {escaped_html};
                            editor.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            return 'ok';
                        }}
                        return 'editor not found';
                    }})()
                """)
                if result == 'ok':
                    print(f"  ✓ 正文已填入 ({len(html)} 字符)")
                else:
                    print(f"  ⚠ 编辑器未找到: {result}")
            except Exception as e:
                print(f"  ❌ 填入正文失败: {e}")

            page.wait_for_timeout(2000)

            # 3. 选择方案
            print("3. 选择方案...")
            try:
                # 点击方案选择器
                plan_trigger = page.locator('text=选择方案').first
                if plan_trigger.is_visible(timeout=3000):
                    plan_trigger.click()
                    page.wait_for_timeout(1000)
                    print("  ✓ 已展开方案下拉")
                else:
                    # 尝试点击包含"方案"的元素
                    page.evaluate('''() => {
                        const els = document.querySelectorAll('div, span, button');
                        for (const el of els) {
                            if (el.textContent.includes('方案')) {
                                el.click();
                                return 'clicked';
                            }
                        }
                        return 'not found';
                    }''')
                    page.wait_for_timeout(1000)
                    print("  ✓ 尝试点击方案区域")

                # 选择指定方案
                plan_result = page.evaluate(f'''() => {{
                    const els = document.querySelectorAll('div, span, li, option');
                    for (const el of els) {{
                        if (el.textContent.trim().includes('{PLAN_NAME}')) {{
                            el.click();
                            return 'selected';
                        }}
                    }}
                    return 'not found';
                }}''')
                page.wait_for_timeout(500)
                if plan_result == 'selected':
                    print(f"  ✓ 已选择方案: {PLAN_NAME}")
                else:
                    print(f"  ⚠ 未找到方案「{PLAN_NAME}」，请手动选择")
            except Exception as e:
                print(f"  ⚠ 方案选择失败: {e}")

            page.wait_for_timeout(1000)

            # 4. 保存为草稿
            print("4. 保存为草稿...")
            try:
                save_result = page.evaluate('''() => {
                    const els = document.querySelectorAll('div, button, span, a');
                    for (const el of els) {
                        if (el.textContent.trim() === '保存为草稿') {
                            el.click();
                            return 'clicked';
                        }
                    }
                    return 'not found';
                }''')
                page.wait_for_timeout(3000)
                if save_result == 'clicked':
                    print("  ✓ 草稿已保存")
                else:
                    print("  ⚠ 未找到「保存为草稿」按钮，请手动保存")
            except Exception as e:
                print(f"  ⚠ 保存失败: {e}")

            # 截图记录
            screenshot_path = "docs/tmp/2026-07-11-ifdian-draft.png"
            page.screenshot(path=screenshot_path)
            print(f"\n📸 截图保存到 {screenshot_path}")

            print("\n" + "=" * 60)
            print("✅ 爱发电草稿处理完成！请到后台确认")
            print(f"   {IFDIAN_EDITOR}")
            print("=" * 60)

        except Exception as e:
            print(f"❌ 出错: {e}")
            try:
                page.screenshot(path="docs/tmp/ifdian_error.png")
                print("  截图保存到 docs/tmp/ifdian_error.png")
            except Exception:
                pass


if __name__ == "__main__":
    main()
