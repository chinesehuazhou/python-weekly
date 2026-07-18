#!/usr/bin/env python3
"""Publish a weekly simplified issue to SSPAI as a draft via existing Edge CDP.

This script intentionally reuses the browser instance that is already running on
localhost:18800. It will not launch or close the browser.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


CDP_URL = "http://localhost:18800"
SSPAI_WRITE_URL = "https://sspai.com/write"
DEFAULT_DESCRIPTION = "每周精选 Python 技术内容，帮助你精进技术与拓展视野"
DEFAULT_TAGS = ["技术", "编程", "互联网", "人工智能"]


class PublishError(RuntimeError):
    """Raised when publishing cannot continue safely."""


def strip_frontmatter(md_text: str) -> str:
    lines = md_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return md_text

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1 :]).strip()
    return md_text


def extract_title_and_body(md_text: str) -> tuple[str, str]:
    body = strip_frontmatter(md_text)
    title = ""
    content_lines: list[str] = []
    found_h1 = False

    for line in body.splitlines():
        if not found_h1 and line.startswith("# ") and not line.startswith("## "):
            title = line[2:].strip()
            found_h1 = True
            continue
        content_lines.append(line)

    cleaned_body = "\n".join(content_lines).strip()
    if not title:
        raise PublishError("未找到 H1 标题，简化版文件需要以 `# 标题` 开头。")
    if not cleaned_body:
        raise PublishError("正文为空，无法创建少数派草稿。")
    return title, cleaned_body


def extract_excerpt(md_text: str) -> str:
    body = strip_frontmatter(md_text)
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        if line.startswith("[") and "](" in line:
            continue
        excerpt = re.sub(r"[*_`>#-]", "", line).strip()
        if excerpt:
            return excerpt[:120]
    return DEFAULT_DESCRIPTION


def collect_image_urls(full_md_text: str) -> list[str]:
    patterns = [
        r"!\[[^\]]*\]\((https?://[^)\s]+)\)",
        r'<img[^>]+src=["\'](https?://[^"\']+)["\']',
        r"\[[^\]]*\]\((https?://[^)\s]+\.(?:png|jpe?g|gif|webp)(?:\?[^)\s]*)?)\)",
        r"(https?://[^\s]+?\.(?:png|jpe?g|gif|webp)(?:\?[^\s]*)?)",
    ]
    urls: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, full_md_text, flags=re.IGNORECASE):
            for group in match.groups():
                if group and group not in urls:
                    urls.append(group)
    return urls


def extract_first_image_url(full_md_text: str) -> str:
    body = strip_frontmatter(full_md_text)
    preferred_scope = body
    for marker in ("## [🐧往年回顾]", "## [🐱欢迎订阅]"):
        if marker in preferred_scope:
            preferred_scope = preferred_scope.split(marker, 1)[0]

    project_scope = ""
    project_markers = ("## [🐿️项目&资源]", "## [🐿️ 项目&资源]")
    for marker in project_markers:
        if marker in preferred_scope:
            project_scope = preferred_scope.split(marker, 1)[1]
            break
    for marker in ("## [🐧往年回顾]", "## [🐱欢迎订阅]"):
        if project_scope and marker in project_scope:
            project_scope = project_scope.split(marker, 1)[0]

    reject_keywords = (
        "python_cat",
        "wechat",
        "weixin",
        "qrcode",
        "qr",
        "xiaobot",
        "coupon",
        "subscribe",
        "promotion",
        "promo",
    )

    def pick(urls: list[str]) -> str | None:
        for url in urls:
            lowered = url.lower()
            if any(keyword in lowered for keyword in reject_keywords):
                continue
            return url
        return None

    project_url = pick(collect_image_urls(project_scope)) if project_scope else None
    if project_url:
        return project_url

    preferred_url = pick(collect_image_urls(preferred_scope))
    if preferred_url:
        return preferred_url

    fallback_url = pick(collect_image_urls(body))
    if fallback_url:
        return fallback_url

    raise PublishError("全文版中未找到正文条目配图，无法为少数派草稿设置封面。")


def md_to_html(md_text: str) -> str:
    result = subprocess.run(
        [
            "pandoc",
            "-f",
            "markdown",
            "-t",
            "html5",
            "--no-highlight",
            "--wrap=none",
            "--quiet",
            "-",
        ],
        input=md_text,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise PublishError(f"pandoc 转换失败: {result.stderr.strip()}")

    html = result.stdout
    html = re.sub(r'<h([23456]) id="[^"]*">', r"<h\1>", html)
    html = re.sub(r"<p>\s*</p>", "", html)
    return html.strip()


def infer_date_str(simple_md_path: Path) -> str:
    match = re.search(r"(\d{4}-\d{2}-\d{2})", simple_md_path.name)
    if not match:
        raise PublishError("无法从文件名中识别日期，请使用 `YYYY-MM-DD-weekly.md` 命名。")
    return match.group(1)


def infer_full_md_path(simple_md_path: Path) -> Path:
    date_str = infer_date_str(simple_md_path)
    candidates = [
        simple_md_path.resolve().parent / "tmp" / f"{date_str}-weekly.md",
        simple_md_path.resolve().parents[2]
        / "astro-blog"
        / "src"
        / "pages"
        / "posts"
        / f"{date_str}-weekly.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def download_image(image_url: str, date_str: str) -> Path:
    parsed = urllib.parse.urlparse(image_url)
    ext = Path(parsed.path).suffix.lower() or ".jpg"
    if ext == ".jpeg":
        ext = ".jpg"

    target = Path(tempfile.gettempdir()) / f"{date_str}-sspai-cover{ext}"
    request = urllib.request.Request(
        image_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0"
            ),
            "Referer": "https://pythoncat.top/",
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(request) as response:
        target.write_bytes(response.read())
    return target


def write_debug_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def click_first_visible(page, selectors: list[str], label: str) -> bool:
    for selector in selectors:
        try:
            locators = page.locator(selector)
            count = locators.count()
            for index in range(count):
                locator = locators.nth(index)
                try:
                    if locator.is_visible(timeout=1000):
                        locator.click(timeout=3000, force=True)
                        print(f"  ✓ {label}: {selector}")
                        return True
                except Exception:
                    continue
        except Exception:
            continue
    return False


def fill_title(page, title: str) -> None:
    selectors = [
        'input[placeholder*="标题"]',
        'textarea[placeholder*="标题"]',
        'input[aria-label*="标题"]',
        'textarea[aria-label*="标题"]',
        'input[name="title"]',
        'textarea[name="title"]',
    ]
    for selector in selectors:
        try:
            locator = page.locator(selector).first
            if locator.count() and locator.is_visible(timeout=1000):
                locator.click(timeout=2000)
                locator.fill("")
                locator.fill(title)
                print(f"  ✓ 标题已填入: {selector}")
                return
        except Exception:
            continue
    raise PublishError("未找到少数派标题输入框。")


def pick_body_editor(page):
    preferred_selectors = [
        '.x-editor-inst[contenteditable="true"]',
        ".ck-editor__editable",
        ".ProseMirror",
        ".ql-editor",
        '[contenteditable="true"][data-placeholder*="正文"]',
        '[contenteditable="true"][aria-label*="正文"]',
    ]
    for selector in preferred_selectors:
        try:
            locator = page.locator(selector).first
            if locator.count() and locator.is_visible(timeout=1000):
                return locator
        except Exception:
            continue

    candidates = page.locator('[contenteditable="true"]')
    best_locator = None
    best_score = -1
    for index in range(candidates.count()):
        locator = candidates.nth(index)
        try:
            if not locator.is_visible(timeout=500):
                continue
            box = locator.bounding_box()
            if not box:
                continue
            score = int(box["width"] * box["height"])
            info = locator.evaluate(
                """(el) => ({
                    text: (el.innerText || '').slice(0, 120),
                    placeholder: el.getAttribute('placeholder') || '',
                    ariaLabel: el.getAttribute('aria-label') || '',
                    className: el.className || '',
                })"""
            )
            title_hint = f"{info['placeholder']} {info['ariaLabel']} {info['className']}"
            if "标题" in title_hint:
                score = -1
            if score > best_score:
                best_score = score
                best_locator = locator
        except Exception:
            continue

    if best_locator:
        return best_locator
    raise PublishError("未找到正文编辑器。")


def set_editor_html(page, locator, html: str) -> None:
    handle = locator.element_handle()
    if handle is None:
        raise PublishError("正文编辑器句柄不可用。")

    # Wait for CKEditor 5 instance to be ready (it initializes asynchronously)
    try:
        page.wait_for_function(
            """(el) => el.ckeditorInstance && typeof el.ckeditorInstance.setData === 'function'""",
            arg=handle,
            timeout=8000,
        )
        print("  ✓ CKEditor 5 实例已就绪")
    except Exception:
        print("  ⚠ CKEditor 实例未在超时内就绪，尝试回退方案")

    inserted_chars = page.evaluate(
        """async ([el, payload]) => {
            el.focus();
            if (el.ckeditorInstance && typeof el.ckeditorInstance.setData === 'function') {
                await el.ckeditorInstance.setData(payload);
                return (el.innerText || '').length;
            }
            if (typeof el.innerHTML === 'string') {
                el.innerHTML = payload;
                el.dispatchEvent(new InputEvent('input', {
                    bubbles: true,
                    inputType: 'insertFromPaste',
                    data: null,
                }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                return (el.innerText || '').length;
            }
            if ('value' in el) {
                el.value = payload;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                return (el.value || '').length;
            }
            return 0;
        }""",
        [handle, html],
    )
    if not inserted_chars:
        raise PublishError("正文内容注入后为空，请检查编辑器结构是否变化。")
    print(f"  ✓ 正文已填入，长度约 {inserted_chars} 字")


def choose_cover_input(page):
    file_inputs = page.locator('input[type="file"]')
    candidates: list[tuple[int, object]] = []
    for index in range(file_inputs.count()):
        locator = file_inputs.nth(index)
        try:
            meta = locator.evaluate(
                """(el) => ({
                    accept: el.getAttribute('accept') || '',
                    name: el.getAttribute('name') || '',
                    id: el.getAttribute('id') || '',
                    className: el.className || '',
                    nearbyText: ((el.closest('form,section,div') || el.parentElement || el).innerText || '').slice(0, 300),
                })"""
            )
        except Exception:
            continue

        score = 0
        text = " ".join(str(value) for value in meta.values())
        if "image" in meta["accept"].lower():
            score += 2
        if any(keyword in text for keyword in ("封面", "题图", "头图", "cover")):
            score += 5
        if any(keyword in text for keyword in ("图片", "上传")):
            score += 1
        candidates.append((score, locator))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def upload_cover(page, image_path: Path) -> bool:
    print("🖼 尝试上传封面...")
    click_first_visible(
        page,
        [
            'button:has-text("封面")',
            'button:has-text("题图")',
            'button:has-text("上传封面")',
            'text=封面',
            'text=题图',
        ],
        "触发封面区域",
    )
    page.wait_for_timeout(1200)

    locator = choose_cover_input(page)
    if locator is None:
        print("  ⚠ 未找到封面上传 input，跳过封面自动上传。")
        return False

    try:
        locator.set_input_files(str(image_path))
        page.wait_for_timeout(2500)
        click_first_visible(
            page,
            [
                'button:has-text("裁切并使用")',
                'button:has-text("确认使用")',
                'button:has-text("确定")',
                'button:has-text("确认")',
                'button:has-text("完成")',
                'button:has-text("保存")',
            ],
            "确认封面上传",
        )
        page.wait_for_timeout(1500)
        print("  ✓ 已尝试上传封面图片")
        return True
    except Exception as exc:
        print(f"  ⚠ 封面上传失败: {exc}")
        return False


def save_draft(page) -> bool:
    print("💾 尝试保存草稿...")
    try:
        result = page.evaluate(
            """async () => {
                const vm = document.querySelector('.attr-form.tag .multiselect')?.__vue__;
                const write = vm?.$parent?.$parent?.$parent;
                if (!write || typeof write.handleSave !== 'function') {
                    return { ok: false, reason: 'write.handleSave unavailable' };
                }
                await write.handleSave();
                return {
                    ok: true,
                    tags: (write.submitData?.tags || []).map(item => item.title || item),
                    customTags: (write.submitData?.custom_tags || []).map(item => item.title || item),
                };
            }"""
        )
        if result.get("ok"):
            page.wait_for_timeout(2000)
            print(
                "  ✓ 已通过页面保存逻辑保存:"
                f" tags={result.get('tags', [])}, custom={result.get('customTags', [])}"
            )
            return True
    except Exception as exc:
        print(f"  ⚠ 页面内置保存失败，回退到按钮点击: {exc}")

    if click_first_visible(
        page,
        [
            'button:has-text("保存")',
            'button:has-text("存草稿")',
            'text=保存',
            'text=存草稿',
        ],
        "保存草稿",
    ):
        page.wait_for_timeout(2000)
        return True
    print("  ⚠ 未找到明确的保存按钮，可能需要手动点一次保存。")
    return False


def set_tags(page, tags: list[str]) -> bool:
    print(f"🏷 尝试设置标签: {', '.join(tags)}")
    try:
        result = page.evaluate(
            """async (titles) => {
                const multiselect = document.querySelector('.attr-form.tag .multiselect');
                const vm = multiselect?.__vue__;
                const tagSelect = vm?.$parent;
                const write = tagSelect?.$parent?.$parent;
                if (!vm || !tagSelect || !write) {
                    return { ok: false, reason: 'tag vue components unavailable' };
                }

                async function resolveExisting(title) {
                    const response = await tagSelect.$http({
                        url: '/matrix/editor/article/tag/search/page/get',
                        method: 'GET',
                        params: { title, offset: 0, limit: 20 },
                    });
                    const items = Array.isArray(response?.data) ? response.data : [];
                    return items.find(item => item.title === title) || null;
                }

                const existing = [];
                const custom = [];
                for (const title of titles) {
                    const found = await resolveExisting(title);
                    if (found) {
                        existing.push(found);
                    } else {
                        custom.push({ id: title, title, custom: true });
                    }
                }

                const combined = existing.concat(custom);
                write.submitData.tags = existing;
                write.submitData.custom_tags = custom;
                tagSelect.tagsList = combined.slice();
                tagSelect.value = combined.slice();
                if (write.$refs['write-sidebar']?.init) {
                    write.$refs['write-sidebar'].init(combined);
                }
                return {
                    ok: true,
                    existing: existing.map(item => item.title || item),
                    custom: custom.map(item => item.title || item),
                    submitTags: (write.submitData.tags || []).map(item => item.title || item),
                    submitCustomTags: (write.submitData.custom_tags || []).map(item => item.title || item),
                    visibleTags: Array.from(
                        document.querySelectorAll('.attr-form.tag .multiselect__tag span:first-child')
                    ).map(el => (el.innerText || '').trim()),
                };
            }""",
            tags,
        )
        if not result.get("ok"):
            print(f"  ⚠ 设置标签失败: {result.get('reason', 'unknown reason')}")
            return False
        print(
            "  ✓ 标签已写入文章模型:"
            f" tags={result.get('submitTags', [])}, custom={result.get('submitCustomTags', [])}"
        )
        print(f"  ✓ 右侧当前显示: {result.get('visibleTags', [])}")
        return True
    except Exception as exc:
        print(f"  ⚠ 设置标签失败: {exc}")
        return False


def find_or_create_sspai_page(context):
    """在已有页签中查找少数派页面，若没有则新建页签。

    不会覆盖或关闭用户已打开的其他网站页签。
    """
    for page in context.pages:
        url = page.url or ""
        if "sspai.com" in url.lower():
            print(f"🔗 找到少数派已有页签: {page.url}")
            return page

    page = context.new_page()
    print("🔗 新建页签用于少数派发布")
    return page


def ensure_editor_ready(page, force_navigate: bool = True) -> None:
    """导航到少数派写作页。

    若当前已在写作页域下且不强制跳转，则跳过导航以避免覆盖已有草稿。
    """
    current_url = (page.url or "").lower()
    already_on_write = "sspai.com/write" in current_url

    if already_on_write and not force_navigate:
        print("📍 已在少数派写作页，跳过导航")
    else:
        page.goto(SSPAI_WRITE_URL, wait_until="load", timeout=30000)

    page.wait_for_timeout(2500)
    current_url = page.url.lower()
    if "login" in current_url:
        raise PublishError("少数派当前未登录，请先在已打开的 Edge 中登录后再重试。")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="将周刊简化版发布到少数派草稿，复用已登录的 Edge 浏览器。"
    )
    parser.add_argument("simple_md", help="简化版 Markdown 文件路径，例如 docs/2026-06-27-weekly.md")
    parser.add_argument(
        "--full-md",
        help="全文版 Markdown 文件路径。默认按日期推断到 astro-blog/src/pages/posts/ 下。",
    )
    parser.add_argument(
        "--keep-body-cover",
        action="store_true",
        help="将封面图同时插入正文顶部，便于在平台封面上传失败时仍保留图片展示。",
    )
    parser.add_argument(
        "--cover-url",
        help="显式指定封面图片 URL，指定后不再自动从全文版中提取。",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    simple_md_path = Path(args.simple_md).resolve()
    if not simple_md_path.exists():
        raise PublishError(f"简化版文件不存在: {simple_md_path}")

    full_md_path = Path(args.full_md).resolve() if args.full_md else infer_full_md_path(simple_md_path)
    if not full_md_path.exists():
        raise PublishError(f"全文版文件不存在: {full_md_path}")

    date_str = infer_date_str(simple_md_path)
    tmp_dir = simple_md_path.parent / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    simple_md = simple_md_path.read_text(encoding="utf-8")
    full_md = full_md_path.read_text(encoding="utf-8")

    title, body_md = extract_title_and_body(simple_md)
    excerpt = extract_excerpt(simple_md)
    cover_url = args.cover_url or extract_first_image_url(full_md)
    cover_path = download_image(cover_url, date_str)

    publish_html = md_to_html(body_md)
    if args.keep_body_cover:
        cover_html = f'<p><img src="{cover_url}" alt="cover"></p>'
        publish_html = f"{cover_html}\n{publish_html}"

    write_debug_file(tmp_dir / f"{date_str}-sspai-body.html", publish_html)
    print(f"📝 标题: {title}")
    print(f"📄 摘要: {excerpt}")
    print(f"🖼 封面: {cover_url}")
    print(f"📦 临时封面文件: {cover_path}")

    draft_url = ""
    screenshot_path = tmp_dir / f"{date_str}-sspai-draft.png"
    debug_path = tmp_dir / f"{date_str}-sspai-draft-url.txt"

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(CDP_URL)
            if not browser.contexts:
                raise PublishError("未检测到已打开的 Edge 上下文，请确认浏览器以 CDP 方式运行。")

            context = browser.contexts[0]
            page = find_or_create_sspai_page(context)

            ensure_editor_ready(page)
            fill_title(page, title)
            body_editor = pick_body_editor(page)
            set_editor_html(page, body_editor, publish_html)
            upload_cover(page, cover_path)
            set_tags(page, DEFAULT_TAGS)
            save_draft(page)

            page.wait_for_timeout(2500)
            draft_url = page.url
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"📍 当前页面: {draft_url}")
            print(f"📸 截图已保存: {screenshot_path}")
    except PlaywrightTimeoutError as exc:
        raise PublishError(f"页面加载或交互超时: {exc}") from exc
    except PlaywrightError as exc:
        raise PublishError(f"Playwright 执行失败: {exc}") from exc

    write_debug_file(debug_path, draft_url)
    metadata = {
        "title": title,
        "excerpt": excerpt,
        "simple_md_path": str(simple_md_path),
        "full_md_path": str(full_md_path),
        "cover_url": cover_url,
        "draft_url": draft_url,
        "screenshot_path": str(screenshot_path),
    }
    write_debug_file(
        tmp_dir / f"{date_str}-sspai-metadata.json",
        json.dumps(metadata, ensure_ascii=False, indent=2),
    )
    print(f"✅ 少数派草稿流程已执行，结果已写入: {debug_path}")

    # 发布成功后清理临时文件
    from cleanup_temp import sspai as _cleanup_sspai
    _cleanup_sspai(date_str)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PublishError as exc:
        print(f"❌ {exc}")
        raise SystemExit(1)
    except urllib.error.URLError as exc:
        print(f"❌ 下载封面失败: {exc}")
        raise SystemExit(1)
