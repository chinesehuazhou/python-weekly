"""通过 CDP 连接正在运行的 Edge 将周刊发布到小报童（保存为草稿）。

不会关闭或重启浏览器，通过 localhost:18800 的 CDP 端口连接已有 Edge。

新增：使用 pandoc 将 Markdown 渲染为 HTML 后再填入编辑器。
"""
import sys
import os
import re
import json
import time
import subprocess
from playwright.sync_api import sync_playwright

# ===== 读取当期日期 =====
date_str = sys.argv[1]  # 格式: YYYY-MM-DD

# ===== 读取准备好的发布内容 =====
content_file = f"docs/tmp/{date_str}-weekly.md"
if not os.path.exists(content_file):
    print(f"❌ 文件不存在: {content_file}")
    sys.exit(1)

with open(content_file, "r", encoding="utf-8") as f:
    raw = f.read()

# 去掉 frontmatter 中的 formatter 字段
lines = raw.split("\n")
clean_lines = []
in_fm = False
fm_started = False
for line in lines:
    if line.strip() == "---":
        if not fm_started:
            fm_started = True
            in_fm = True
            clean_lines.append(line)
            continue
        else:
            in_fm = False
            clean_lines.append(line)
            continue
    if in_fm:
        skip_prefixes = [
            "layout:", "author:", "tags:", "theme:", "featured:"
        ]
        if any(line.strip().startswith(p) for p in skip_prefixes):
            continue
        clean_lines.append(line)
    else:
        clean_lines.append(line)

publish_md = "\n".join(clean_lines)

# ===== 使用 pandoc 将 Markdown 渲染为 HTML =====
print("🔄 使用 pandoc 渲染 Markdown → HTML...")
result = subprocess.run([
    "pandoc", "-f", "markdown", "-t", "html5",
    "--no-highlight", "--wrap=none", "--quiet",
    "-",  # read from stdin
], input=publish_md, capture_output=True, text=True)

if result.returncode != 0:
    print(f"❌ pandoc 转换失败: {result.stderr}")
    sys.exit(1)

publish_html = result.stdout

# 清洗 HTML：去掉 h2 的 id 属性，去掉空段落
publish_html = re.sub(r'<h2 id="[^"]*">', '<h2>', publish_html)
publish_html = re.sub(r'<p>\s*</p>', '', publish_html)
publish_html = publish_html.strip()

# 提取标题和描述
title_match = re.search(r"title:\s*['\"](.+?)['\"]", raw)
title = title_match.group(1) if title_match else "Python 潮流周刊"
desc_match = re.search(r"description:\s*['\"](.+?)['\"]", raw)
description = desc_match.group(1) if desc_match else ""

print(f"📝 准备发布: {title}")
print(f"📏 Markdown 长度: {len(publish_md)} 字符 → HTML 长度: {len(publish_html)} 字符")

# ===== 通过 CDP 连接已运行的 Edge =====
CDP_URL = "http://localhost:18800"
XIAOBOT_CREATOR = "https://xiaobot.net/creator/python_weekly/published"

draft_url = None

with sync_playwright() as p:
    print("🔗 通过 CDP 连接已有 Edge...")
    browser = p.chromium.connect_over_cdp(CDP_URL)

    # 获取或创建页面
    if browser.contexts:
        context = browser.contexts[0]
        pages = context.pages
        if pages:
            page = pages[0]
            print(f"  ✓ 已有页面: {page.url[:80]}")
        else:
            page = context.new_page()
    else:
        context = browser.new_context()
        page = context.new_page()

    try:
        # 1. 导航到创作者中心
        print("🌐 导航到小报童创作者中心...")
        page.goto(XIAOBOT_CREATOR, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        # 检查登录
        page_text = page.content()
        if "login" in page.url.lower() or "扫码" in page_text:
            print("⚠️ 小报童登录已失效！请先在 Edge 中扫码登录，然后按 Enter...")
            input()
            page.goto(XIAOBOT_CREATOR, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)

        # 2. 点击「发布新内容」
        print("🔘 点击「发布新内容」...")
        publish_btn_selectors = [
            "text=发布新内容",
            "text=新建文章",
            "text=新建",
            "button:has-text('发布')",
            "a:has-text('发布')",
        ]
        clicked = False
        for selector in publish_btn_selectors:
            try:
                page.click(selector, timeout=5000)
                clicked = True
                print(f"  ✓ 点击: {selector}")
                break
            except Exception:
                continue

        if not clicked:
            print("⚠️ 自动点击失败，请在浏览器中手动点击「发布新内容」，然后按 Enter...")
            input()

        page.wait_for_timeout(3000)
        print(f"  📍 当前页面: {page.url[:100]}")

        # 3. 查找标题输入框并填入
        if title_from_fm := title_match.group(1) if title_match else None:
            # 标题栏可能是 textarea 或 input
            title_selectors = [
                'textarea[placeholder*="标题"]',
                'input[placeholder*="标题"]',
                'input[name="title"]',
                "#title",
                ".title-input",
            ]
            for ts in title_selectors:
                try:
                    tel = page.locator(ts).first
                    if tel.is_visible(timeout=2000):
                        tel.click()
                        page.keyboard.press("Meta+a")
                        page.keyboard.press("Backspace")
                        tel.fill(title_from_fm)
                        print(f"  ✓ 标题已填")
                        break
                except Exception:
                    pass

        # 4. 查找编辑器并通过 JavaScript 设置 HTML 内容
        print("📝 查找编辑器并填入 HTML 内容...")
        editor_selectors = [
            "[contenteditable='true']",
            ".ql-editor",
            ".ProseMirror",
            ".editor-content",
            "#editor",
            "[role='textbox']",
        ]

        editor_found = False
        for selector in editor_selectors:
            try:
                el = page.locator(selector).first
                if el.is_visible(timeout=2000):
                    # 转义 HTML 用于 JavaScript
                    escaped_html = json.dumps(publish_html)
                    page.evaluate(f"""
                        (function() {{
                            const editor = document.querySelector('{selector}');
                            if (editor) {{
                                editor.focus();
                                editor.innerHTML = {escaped_html};
                                editor.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            }}
                        }})()
                    """)
                    print(f"  ✓ 通过 {selector} 填入 HTML ({len(publish_html)} 字符)")
                    editor_found = True
                    break
            except Exception as e:
                print(f"  ⚠ {selector}: {e}")
                continue

        if not editor_found:
            print("⚠️ 未找到编辑器，请手动粘贴内容后按 Enter...")
            import subprocess as sp
            sp.run(["pbcopy"], input=publish_md.encode())
            print("  原始 Markdown 已复制到剪贴板，Cmd+V 粘贴即可")
            input()

        page.wait_for_timeout(2000)

        # 5. 保存草稿
        print("💾 查找保存草稿按钮...")
        save_selectors = [
            "text=存草稿",
            "text=保存草稿",
            "button:has-text('草稿')",
            "[data-action='draft']",
        ]
        saved = False
        for selector in save_selectors:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=3000):
                    # 先确认内容已加载完成
                    page.wait_for_timeout(1000)
                    btn.click()
                    saved = True
                    print(f"  ✓ 点击: {selector}")
                    break
            except Exception:
                continue

        if not saved:
            # 回退：尝试用文本查找
            try:
                page.locator("text=存草稿").first.click(timeout=3000)
                saved = True
                print("  ✓ 点击: 存草稿 (文本匹配)")
            except Exception:
                pass

        if not saved:
            print("⚠️ 未找到保存草稿按钮，请手动点击后按 Enter...")
            input()

        page.wait_for_timeout(4000)

        # 6. 提取草稿链接
        current_url = page.url
        print(f"📍 当前 URL: {current_url}")
        post_match = re.search(r"/post/([a-f0-9-]+)", current_url)
        if post_match:
            post_id = post_match.group(1)
            draft_url = f"https://xiaobot.net/post/{post_id}"
        else:
            # 从页面找链接
            try:
                links = page.locator('a[href*="/post/"]').all()
                for link in links:
                    href = link.get_attribute("href") or ""
                    m = re.search(r"/post/([a-f0-9-]+)", href)
                    if m:
                        draft_url = f"https://xiaobot.net/post/{m.group(1)}"
                        break
            except Exception:
                pass

        # 如果还没找到，尝试点击编辑链接来获取 UUID
        if not draft_url:
            print("📋 尝试从内容列表获取草稿链接...")
            try:
                # 在列表中找包含标题文本的 generic 元素（草稿没有 link）
                draft_row = page.locator(f"text={title_from_fm[:20]}").first
                if draft_row:
                    draft_row.click()
                    page.wait_for_timeout(2000)
                    edit_url = page.url
                    m = re.search(r"/edit/([a-f0-9-]+)", edit_url)
                    if m:
                        draft_url = f"https://xiaobot.net/post/{m.group(1)}"
            except Exception:
                pass

    except Exception as e:
        print(f"❌ 出错: {e}")
        try:
            page.screenshot(path="xiaobot_error.png")
            print("  截图保存到 xiaobot_error.png")
        except Exception:
            pass

# 输出结果
if draft_url:
    print(f"\n🎯 草稿链接: {draft_url}")
    with open(f"docs/tmp/{date_str}-xiaobot-url.txt", "w") as f:
        f.write(draft_url)
    print(f"  已写入 docs/tmp/{date_str}-xiaobot-url.txt")

    # 发布成功后清理临时文件（删除刚写入的 txt 本身）
    from cleanup_temp import xiaobot as _cleanup_xiaobot
    _cleanup_xiaobot(date_str)
else:
    print("\n⚠️ 未能自动获取草稿链接")
    print("请从浏览器地址栏复制草稿链接粘贴后按 Enter:")
    draft_url = input().strip()
    if draft_url:
        with open(f"docs/tmp/{date_str}-xiaobot-url.txt", "w") as f:
            f.write(draft_url)
        print(f"  已写入 docs/tmp/{date_str}-xiaobot-url.txt")
        from cleanup_temp import xiaobot as _cleanup_xiaobot
        _cleanup_xiaobot(date_str)
    else:
        print("\n❌ 未获取到链接")
        sys.exit(1)
