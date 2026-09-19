"""通过 CDP 连接正在运行的 Edge 将周刊发布到小报童。

不会关闭或重启浏览器，通过 localhost:18800 的 CDP 端口连接已有 Edge。

默认直接「发布」为正式文章（加 --draft 则仅存草稿，用于验证排版）。
--publish-existing <uuid|url> 把已经建好的草稿直接发布，不新建内容。

使用 pandoc 将 Markdown 渲染为 HTML 后再填入编辑器。

发布链接的提取方式：发布后回到创作中心列表，按标题定位该行，读取其
a[href="/post/{uuid}"]。注意不能用「页面上第一个 /post/ 链接」，那会命中列表里
其它文章（曾因此记错链接）。

发布后的公开链接写入 docs/tmp/YYYY-MM-DD-xiaobot-url.txt 且**不再清理**，
供后续「全文链接回填」使用。
"""
import sys
import os
import re
import json
import subprocess
from playwright.sync_api import sync_playwright

# ===== 解析参数 =====
argv = sys.argv[1:]
draft_mode = "--draft" in argv
publish_existing = None
if "--publish-existing" in argv:
    i = argv.index("--publish-existing")
    if i + 1 < len(argv):
        publish_existing = argv[i + 1]
    del argv[i:i + 2]
while "--draft" in argv:
    argv.remove("--draft")

if not argv:
    print("用法: xiaobot_publish.py YYYY-MM-DD [--draft] [--publish-existing <uuid|url>]")
    sys.exit(1)

date_str = argv[0]  # 格式: YYYY-MM-DD

# ===== 准备发布内容 =====
publish_html = ""
title = ""
title_from_fm = ""

if not publish_existing:
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
    title_from_fm = title

    print(f"📝 准备{'存草稿' if draft_mode else '发布'}: {title}")
    print(f"📏 Markdown 长度: {len(publish_md)} 字符 → HTML 长度: {len(publish_html)} 字符")
else:
    print(f"♻️  发布已有草稿: {publish_existing}")

# ===== 通过 CDP 连接已运行的 Edge =====
CDP_URL = "http://localhost:18800"
XIAOBOT_CREATOR = "https://xiaobot.net/creator/python_weekly/published"

UUID_RE = re.compile(r"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})")


def extract_uuid(value: str) -> str | None:
    m = UUID_RE.search(value or "")
    return m.group(1) if m else None


def find_post_link(page, title: str, timeout_ms: int = 20000) -> str | None:
    """在创作中心列表里按标题定位该行，返回 https://xiaobot.net/post/{uuid}。

    已发布行的标题外层是 a[href="/post/{uuid}"]；草稿行 href 为空。
    """
    key = None
    m = re.search(r"#(\d+)", title or "")
    key = f"#{m.group(1)}" if m else (title or "")[:12]
    if not key:
        return None

    waited = 0
    while waited < timeout_ms:
        href = page.evaluate("""(key) => {
            const lines = [...document.querySelectorAll('.content-title-line')];
            const line = lines.find(l => (l.innerText || '').includes(key));
            if (!line) return '';
            const a = line.closest('a');
            const h = a ? (a.getAttribute('href') || '') : '';
            return h.includes('/post/') ? h : '';
        }""", key)
        u = extract_uuid(href)
        if u:
            return f"https://xiaobot.net/post/{u}"
        page.wait_for_timeout(1000)
        waited += 1000
    return None


def click_action(page, label: str) -> str:
    """点击「发布」或「存草稿」，并处理可能出现的二次确认弹窗。

    返回命中的元素描述；未找到返回空串。
    """
    hit = page.evaluate("""(label) => {
        const els = [...document.querySelectorAll('button, a, [role=button]')];
        const el = els.find(e => (e.innerText || '').trim() === label
                                 && e.getBoundingClientRect().width > 0);
        if (el) { el.click(); return (el.className || el.tagName).toString(); }
        return '';
    }""", label)

    if not hit:
        # 回退：发布按钮有稳定的 class
        sel = ".publishBtn" if label == "发布" else "text=存草稿"
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=3000):
                el.click()
                hit = sel
        except Exception:
            pass

    if not hit:
        return ""

    print(f"  ✓ 点击: {label}（{hit[:40]}）")
    page.wait_for_timeout(1500)

    for _ in range(3):
        confirmed = page.evaluate("""() => {
            const scope = document.querySelector('.el-message-box, .el-dialog, [role=dialog]');
            if (!scope) return '';
            const els = [...scope.querySelectorAll('button, [role=button]')];
            const el = els.find(e => ['确认', '确定', '确认发布', '继续']
                                     .includes((e.innerText || '').trim())
                                     && e.getBoundingClientRect().width > 0);
            if (el) { el.click(); return el.innerText.trim(); }
            return '';
        }""")
        if not confirmed:
            break
        print(f"  ✓ 二次确认: {confirmed}")
        page.wait_for_timeout(1500)

    return hit


public_url = None

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
        if publish_existing:
            # ===== 模式 A：发布已存在的草稿 =====
            target = publish_existing
            if not target.startswith("http"):
                target = f"https://xiaobot.net/creator/python_weekly/edit/{target}"
            print("🌐 打开已有草稿...")
            page.goto(target, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)

            title = page.evaluate(
                "() => {const t = document.querySelector('textarea, input[placeholder*=标题]');"
                " return t ? t.value : '';}"
            ) or ""
            body_len = page.evaluate(
                "() => {const e = document.querySelector('[contenteditable=true]');"
                " return e ? e.innerText.length : 0;}"
            )
            print(f"  ✓ 草稿标题: {title[:60]}")
            print(f"  ✓ 正文长度: {body_len} 字")
            if body_len < 500:
                print("⚠️ 正文内容偏少，请确认无误后再发布")

            print("🚀 点击发布...")
            if not click_action(page, "发布"):
                print("⚠️ 未找到发布按钮，请手动点击后按 Enter...")
                input()
            page.wait_for_timeout(4000)
        else:
            # ===== 模式 B：新建并发布 =====
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

            # 点击「发布新内容」
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

            # 填标题
            if title_from_fm:
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
                            print("  ✓ 标题已填")
                            break
                    except Exception:
                        pass

            # 填正文
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
                subprocess.run(["pbcopy"], input=publish_md.encode())
                print("  原始 Markdown 已复制到剪贴板，Cmd+V 粘贴即可")
                input()

            page.wait_for_timeout(2000)

            # 发布 / 存草稿
            label = "存草稿" if draft_mode else "发布"
            print(f"{'💾' if draft_mode else '🚀'} 点击「{label}」...")
            if not click_action(page, label):
                print(f"⚠️ 未找到「{label}」按钮，请手动点击后按 Enter...")
                input()
            page.wait_for_timeout(4000)

        # ===== 提取发布链接 =====
        print(f"📍 当前 URL: {page.url}")
        if "published" not in page.url:
            page.goto(XIAOBOT_CREATOR, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)
        else:
            # 发布后 SPA 会跳回列表页，但 DOM 可能是发布前的旧快照
            # （新行还没有 href），必须强制刷新一次再定位。
            page.reload(wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2500)

        public_url = find_post_link(page, title) if title else None
        if public_url:
            print(f"  ✓ 从列表定位到: {public_url}")
        else:
            # 回退：从编辑页 URL 取 UUID（未发布时 href 为空）
            uid = extract_uuid(page.url)
            if uid:
                public_url = f"https://xiaobot.net/post/{uid}"

    except Exception as e:
        print(f"❌ 出错: {e}")
        try:
            page.screenshot(path="xiaobot_error.png")
            print("  截图保存到 xiaobot_error.png")
        except Exception:
            pass

# ===== 输出结果 =====
url_file = f"docs/tmp/{date_str}-xiaobot-url.txt"

if public_url:
    kind = "草稿" if draft_mode else "正式发布"
    print(f"\n🎯 {kind}链接: {public_url}")
    with open(url_file, "w") as f:
        f.write(public_url)
    print(f"  已写入 {url_file}（保留，供全文链接回填使用）")
    if not draft_mode:
        print("\n👉 下一步：把该链接回填到简化版 2 处 × 2 文件（python-weekly + astro-blog）")
else:
    print(f"\n⚠️ 未能自动获取链接")
    print("请从浏览器地址栏复制链接粘贴后按 Enter:")
    pasted = input().strip()
    if pasted:
        with open(url_file, "w") as f:
            f.write(pasted)
        print(f"  已写入 {url_file}")
    else:
        print("\n❌ 未获取到链接")
        sys.exit(1)
