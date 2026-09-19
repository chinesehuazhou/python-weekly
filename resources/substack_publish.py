"""通过 CDP 连接正在运行的 Edge 将周刊简化版发布到 Substack。

默认**创建后直接发布**（Continue → Send to everyone now）；加 `--draft-only`
则只存草稿、不点发布。

不会关闭或重启浏览器，通过 localhost:18800 的 CDP 端口连接已有 Edge。

使用 pandoc 将 Markdown 渲染为 HTML 后填入 TipTap 编辑器。

用法:
    # 创建并发布
    .venv/bin/python resources/substack_publish.py docs/YYYY-MM-DD-weekly.md

    # 只存草稿
    .venv/bin/python resources/substack_publish.py docs/YYYY-MM-DD-weekly.md --draft-only

    # 更新已有草稿
    .venv/bin/python resources/substack_publish.py docs/YYYY-MM-DD-weekly.md --draft-url https://pythoncat.substack.com/publish/post/123456

⚠️ 发布动作会立即公开并推送订阅者，不可撤回。
"""
import sys
import os
import re
import json
import subprocess
from playwright.sync_api import sync_playwright

CDP_URL = "http://localhost:18800"
SUBSTACK_DRAFTS = "https://pythoncat.substack.com/publish/posts/drafts"
DEFAULT_SUBTITLE = "每周精选 Python 技术内容，精进技术，增长收入"
SECTION_NAME = "Python潮流周刊"


def strip_frontmatter(md_text: str) -> str:
    """去掉 frontmatter，只保留正文 Markdown。"""
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


def extract_title_from_md(md_text: str) -> tuple[str, str]:
    """从 Markdown 提取标题和正文（去掉 H1 标题行）。

    Returns:
        (title, body_md): 标题和去掉 H1 后的正文
    """
    body = strip_frontmatter(md_text)
    title = ""
    lines = body.split("\n")
    new_lines = []
    found_h1 = False

    for line in lines:
        if not found_h1 and line.startswith("# ") and not line.startswith("## "):
            title = line[2:].strip()
            found_h1 = True
            continue
        new_lines.append(line)

    body_without_h1 = "\n".join(new_lines).strip()
    return title, body_without_h1


def md_to_html(md_text: str) -> str:
    """使用 pandoc 将 Markdown 转为 HTML。"""
    result = subprocess.run([
        "pandoc", "-f", "markdown", "-t", "html5",
        "--no-highlight", "--wrap=none", "--quiet",
        "-",
    ], input=md_text, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ pandoc 转换失败: {result.stderr}")
        sys.exit(1)

    html = result.stdout

    # 清洗 HTML
    html = re.sub(r'<h2 id="[^"]*">', '<h2>', html)
    html = re.sub(r'<p>\s*</p>', '', html)
    html = html.strip()

    return html


def find_or_create_substack_page(context, draft_url: str | None = None):
    """在已有页签中查找 Substack 页面，若没有则新建页签。

    若提供 draft_url，优先复用已打开该 URL 的页签。
    不会覆盖或关闭用户已打开的其他网站页签。
    """
    # 优先：精确匹配 draft_url
    if draft_url:
        for page in context.pages:
            if draft_url in (page.url or ""):
                print(f"🔗 找到已有草稿页签: {page.url}")
                return page

    # 其次：查找 Substack 编辑器页面（排除草稿列表和详情页）
    for page in context.pages:
        url = page.url or ""
        if "substack.com/publish/post" in url and "drafts" not in url and "detail" not in url:
            print(f"🔗 找到 Substack 编辑页签: {page.url}")
            return page

    # 再次：查找任意 Substack 页面
    for page in context.pages:
        if "substack.com" in (page.url or "").lower():
            print(f"🔗 找到 Substack 已有页签: {page.url}")
            return page

    # 没有则新建
    page = context.new_page()
    print("🔗 新建页签用于 Substack 发布")
    return page


def publish_post(page) -> str | None:
    """在编辑器里点右上「Continue」→ 弹窗底部「Send to everyone now」→ 发布。返回线上链接。

    2026-09 改版后 Substack 编辑页右上角不再是「Publish」而是「Continue」，
    点开是一个全屏 Publish 弹窗（Audience / Allow comments from… / This post
    belongs in… / Add tags / Social preview / Delivery），底部两个按钮：
    Cancel 与 **Send to everyone now**。

    ⚠️ 这一步会**立即公开并推送给订阅者**，不可撤回。
    """
    print("\n9. 发布（Continue → Send to everyone now）...")
    page.get_by_role("button", name="Continue", exact=True).first.click()
    page.wait_for_timeout(5000)

    confirm = page.locator("button:has-text('Send to everyone now')")
    if not confirm.count():
        print("  ✗ 未出现发布弹窗（找不到「Send to everyone now」），已中止发布；草稿仍保留")
        page.screenshot(path="/tmp/substack_publish_missing.png")
        return None

    page.screenshot(path="/tmp/substack_publish_dialog.png")
    # 发布前把弹窗里的关键设置打出来，便于事后核对
    settings = page.evaluate('''() => {
        const vis = e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
        const picked = [...document.querySelectorAll('input[type=radio]')]
            .filter(r => vis(r) && r.checked)
            .map(r => ((r.closest('label') || {}).innerText || '').replace(/\\s+/g,' ').trim());
        const section = [...document.querySelectorAll('button, [role=combobox]')]
            .filter(vis).map(e => (e.innerText||'').replace(/\\s+/g,' ').trim())
            .find(t => t.includes('潮流周刊')) || '';
        return { picked, section };
    }''')
    print(f"  · 受众/评论等已选项: {settings.get('picked')}")
    print(f"  · Section: {settings.get('section')}")

    confirm.first.click()
    print("  ✓ 已点「Send to everyone now」，等待结果…")
    page.wait_for_timeout(15000)
    page.screenshot(path="/tmp/substack_after_publish.png")

    body = page.evaluate("() => (document.body.innerText || '')")
    if "Your post is live" in body:
        print("  ✅ Substack 显示「Your post is live!」")
    else:
        print("  ⚠ 未看到「Your post is live!」，请人工确认发布状态")

    # 发布后落到 share-center，真正的公开链接在页面里的 input 中
    live = page.evaluate('''() => {
        for (const inp of document.querySelectorAll('input, textarea')) {
            const v = inp.value || '';
            if (v.includes('substack.com/p/')) return v;
        }
        const a = document.querySelector('link[rel=canonical]');
        return a ? a.href : '';
    }''')
    print(f"  · 当前 URL: {page.url}")
    if live and "substack.com/p/" in live:
        print(f"  · 公开链接: {live}")
        return live
    return page.url


def main():
    if len(sys.argv) < 2:
        print("用法: python substack_publish.py <weekly_md_path> [--draft-url <url>]")
        sys.exit(1)

    md_path = sys.argv[1]
    existing_draft_url = None
    draft_only = False

    # 解析 --draft-url 参数
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--draft-url" and i + 1 < len(args):
            existing_draft_url = args[i + 1]
            i += 2
        elif args[i] == "--draft-only":
            draft_only = True
            i += 1
        else:
            print(f"⚠ 未知参数: {args[i]}")
            i += 1

    if not os.path.exists(md_path):
        print(f"❌ 文件不存在: {md_path}")
        sys.exit(1)

    with open(md_path, "r", encoding="utf-8") as f:
        raw = f.read()

    # 提取标题和正文
    full_title, body_md = extract_title_from_md(raw)
    if not full_title:
        print("❌ 未找到标题（需要以 # 开头的 H1 标题）")
        sys.exit(1)

    print(f"📝 标题: {full_title}")

    # pandoc 转换
    print("🔄 使用 pandoc 渲染 Markdown → HTML...")
    publish_html = md_to_html(body_md)

    print(f"📏 HTML 长度: {len(publish_html)} 字符")

    # 提取日期
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", md_path)
    date_str = date_match.group(1) if date_match else "unknown"

    draft_url = None
    post_edit_url = None
    published_url = None

    with sync_playwright() as p:
        print("🔗 通过 CDP 连接已有 Edge...")
        browser = p.chromium.connect_over_cdp(CDP_URL)

        if not browser.contexts:
            print("❌ 没有打开的浏览器上下文")
            sys.exit(1)

        context = browser.contexts[0]

        # 始终创建新草稿（不复用已有编辑器页面）
        if existing_draft_url:
            print(f"🌐 打开已有草稿: {existing_draft_url}")
            page = find_or_create_substack_page(context, draft_url=existing_draft_url)
            if existing_draft_url not in (page.url or ""):
                page.goto(existing_draft_url, wait_until="load", timeout=30000)
            page.wait_for_timeout(3000)
        else:
            print("🌐 创建新草稿...")
            page = find_or_create_substack_page(context)

            # 先导航到草稿列表
            page.goto(SUBSTACK_DRAFTS, wait_until="load", timeout=30000)
            page.wait_for_timeout(3000)

            # 检查登录
            if "login" in page.url.lower():
                print("⚠️ Substack 登录已失效！请先在 Edge 中登录，然后按 Enter...")
                input()
                page.goto(SUBSTACK_DRAFTS, wait_until="load", timeout=30000)
                page.wait_for_timeout(3000)

            # 点击 Create → Article
            # 注意：Create 下拉里的 Article 是 <a class="item-Npdq6R">，
            # 用 `text=Article` 会先命中侧边栏等隐藏同名节点导致超时，
            # 故遍历可见元素取精确文本匹配。
            try:
                page.locator('button:has-text("Create")').first.click(timeout=5000)
                page.wait_for_timeout(1500)
                clicked = page.evaluate('''() => {
                    const els = [...document.querySelectorAll('a, button, div')];
                    const el = els.find(e => (e.innerText || '').trim() === 'Article'
                                             && e.getBoundingClientRect().width > 0);
                    if (el) { el.click(); return el.tagName + '.' + el.className; }
                    return '';
                }''')
                if not clicked:
                    raise RuntimeError("未找到可见的 Create → Article 菜单项")
                page.wait_for_timeout(5000)
                print(f"  ✓ 新草稿已创建（menu: {clicked[:40]}）")
            except Exception as e:
                print(f"⚠ 自动创建草稿失败: {e}")
                print("请手动在浏览器中点击 Create → Article，然后按 Enter...")
                input()
                page = find_or_create_substack_page(context)

        # 获取 post ID
        post_id_match = re.search(r"/post/(\d+)", page.url)
        post_id = post_id_match.group(1) if post_id_match else None
        print(f"📋 Post ID: {post_id}")
        post_edit_url = page.url

        page.wait_for_timeout(2000)

        try:
            # 1. 关闭 File Settings 弹窗（如果打开）
            print("\n1. 关闭 File Settings 弹窗...")
            try:
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)
                print("  ✓ 已按 Escape")
            except Exception:
                pass

            # 2. 填入主标题
            print("2. 填入主标题...")
            try:
                title_input = page.locator('textarea[placeholder="Title"]')
                title_input.click()
                page.wait_for_timeout(300)
                # 全选并替换
                title_input.fill("")
                title_input.fill(full_title)
                page.wait_for_timeout(500)
                print(f"  ✓ 标题已填: {full_title[:50]}")
            except Exception as e:
                print(f"  ⚠ 填入标题失败: {e}")

            # 3. 填入副标题
            print("3. 填入副标题...")
            try:
                subtitle_input = page.locator('textarea[placeholder="Add a subtitle…"]')
                subtitle_input.click()
                page.wait_for_timeout(300)
                subtitle_input.fill("")
                subtitle_input.fill(DEFAULT_SUBTITLE)
                page.wait_for_timeout(500)
                print(f"  ✓ 副标题已填: {DEFAULT_SUBTITLE}")
            except Exception as e:
                print(f"  ⚠ 填入副标题失败: {e}")

            # 4. 通过 JavaScript 设置编辑器内容
            print("4. 设置编辑器内容（TipTap/ProseMirror）...")
            try:
                escaped_html = json.dumps(publish_html)
                result = page.evaluate(f"""
                    (function() {{
                        const editor = document.querySelector('.tiptap.ProseMirror[contenteditable="true"]');
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
                    print(f"  ✓ 编辑器内容已设置 ({len(publish_html)} 字符)")
                else:
                    print(f"  ⚠ 编辑器未找到: {result}")
            except Exception as e:
                print(f"  ❌ 设置内容失败: {e}")
                # Fallback: copy to clipboard
                subprocess.run(["pbcopy"], input=body_md.encode())
                print("  原始 Markdown 已复制到剪贴板，请手动粘贴")
                input("  粘贴完成后按 Enter 继续...")

            # 5. 选择 Section
            # 改版后 Section 不再是 <select>，而是工具栏「Choose a section」按钮 +
            # 下拉菜单（菜单项 class=item-Npdq6R）；用精确文本匹配，避免误选英文号。
            print("\n5. 选择 Section...")
            page.wait_for_timeout(2000)  # 等待自动保存

            def click_section() -> bool:
                return page.evaluate(
                    """(name) => {
                        const els = [...document.querySelectorAll('button, a, div')];
                        const el = els.find(e => (e.innerText || '').trim() === name
                                                 && e.getBoundingClientRect().width > 0);
                        if (el) { el.click(); return true; }
                        return false;
                    }""",
                    SECTION_NAME,
                )

            try:
                if not click_section():
                    page.locator('button:has-text("Choose a section")').first.click(timeout=6000)
                    page.wait_for_timeout(1800)
                    click_section()
                page.wait_for_timeout(1500)
                page.keyboard.press("Escape")
                page.wait_for_timeout(800)
                print(f"  ✓ Section: {SECTION_NAME}")
            except Exception as e:
                print(f"  ⚠ 选择 Section 失败: {e}")

            # 6. 打开 Post Settings
            # 注意：工具栏的 Settings 是普通 button（页面里没有 role="tab"），
            # 旧的 `[role="tab"]` 定位已失效。
            print("6. 打开 Post Settings...")
            try:
                page.locator('button:has-text("Settings")').last.click(timeout=6000)
                page.wait_for_timeout(2500)
                print("  ✓ Post Settings 已打开")
            except Exception as e:
                print(f"  ⚠ 打开 Post Settings 失败: {e}")

            # 7. 提取草稿链接（从 input 中找包含 /p/ 的链接）
            print("7. 提取草稿链接...")
            try:
                draft_link = page.evaluate('''() => {
                    const inputs = document.querySelectorAll('input');
                    for (const inp of inputs) {
                        const val = inp.value || '';
                        if (val.includes('/p/') && val.includes('substack.com')) {
                            return val;
                        }
                    }
                    return null;
                }''')

                if draft_link:
                    draft_url = draft_link
                    print(f"  ✓ 草稿链接: {draft_url}")
                else:
                    print("  ⚠ 未能自动提取草稿链接")
            except Exception as e:
                print(f"  ⚠ 提取草稿链接失败: {e}")

            # 8. 关闭评论
            # 选项行内含「New」角标，故 textContent 不等于 'No one (disable comments)'，
            # 需用前缀匹配并点该 label 下的 radio。
            print("8. 配置评论设置...")
            try:
                comments_result = page.evaluate('''() => {
                    for (const label of document.querySelectorAll('label')) {
                        if ((label.innerText || '').trim().startsWith('No one (disable comments)')) {
                            (label.querySelector('input[type=radio]') || label).click();
                            return 'disabled';
                        }
                    }
                    return 'not found';
                }''')
                page.wait_for_timeout(1200)
                print(f"  ✓ 评论: {comments_result}")
            except Exception:
                print("  ⚠ 评论设置跳过（可能已配置）")

            # 9. 关闭 Post Settings
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)

            print("\n⏳ 等待 Substack 自动保存...")
            page.wait_for_timeout(3000)

            print("✅ 草稿已保存（Substack 自动保存）")

            # 10. 最终检查
            saved_indicator = page.evaluate('''() => {
                const el = document.querySelector('[class*="Saved"], [class*="saved"], [class*="save-indicator"]');
                return el ? el.textContent?.trim() : 'unknown';
            }''')
            print(f"💾 保存状态: {saved_indicator}")

            # 11. 发布（默认；--draft-only 则停在草稿）
            if draft_only:
                print("\n⏭ --draft-only：跳过发布，草稿留在 Substack 后台")
            else:
                published_url = publish_post(page)

        except Exception as e:
            print(f"❌ 出错: {e}")
            try:
                page.screenshot(path="/tmp/substack_error.png")
                print("  截图保存到 /tmp/substack_error.png")
            except Exception:
                pass

    # 输出结果
    print()
    if published_url and "substack.com/p/" in published_url and "publish" not in published_url:
        print(f"🎯 已发布: {published_url}")
        url_file = f"docs/tmp/{date_str}-substack-url.txt"
        with open(url_file, "w") as f:
            f.write(published_url)
        print(f"  已写入 {url_file}")
        print("  ⚠ 发布后请打开该链接复核一次（脚本只依据页面上的「Your post is live!」判断）")
    elif draft_url:
        print(f"🎯 草稿链接: {draft_url}")
        url_file = f"docs/tmp/{date_str}-substack-url.txt"
        with open(url_file, "w") as f:
            f.write(draft_url)
        print(f"  已写入 {url_file}")
        print("  📌 未确认发布成功：若已发布，请用草稿链接/后台核对线上地址")
    else:
        print(f"⚠️ 未能获取草稿链接")
        if post_edit_url:
            print(f"  编辑页面: {post_edit_url}")
            print(f"  请从 Post Settings → Secret draft link 手动复制")

    if post_edit_url:
        print(f"📝 编辑链接: {post_edit_url}")


if __name__ == "__main__":
    main()
