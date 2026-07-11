#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""翻译文章发布到微信公众号草稿箱。

用法：
  python3 resources/publish_article.py <markdown_file> [选项]

与 wechat_publish.py（周刊专用）不同，此脚本针对翻译文章做了专门处理：
  - 正文不包含 H1 标题（标题由 API 单独设置）
  - 移除 --- 分隔线（避免微信渲染为多余空白）
  - 去除标签间空白（微信编辑器会渲染为可见空白）
  - 自动插入引导关注头部、版权信息、推广尾部

示例：
  python3 resources/publish_article.py /tmp/article-final-v3.md \
    --title "标题" --author "豌豆花" \
    --orig-author "Perplexity Research" \
    --orig-title "Rethinking Search as Code Generation" \
    --source-url "https://..."
"""

import os, re, sys, json, time, argparse
from pathlib import Path
from datetime import datetime

import httpx
from dotenv import load_dotenv
import inkpress
from pygments.formatters import HtmlFormatter

# ===== 加载配置 =====
load_dotenv(Path(__file__).resolve().parent / ".env")

WECHAT_APP_ID = os.getenv("WECHAT_APP_ID")
WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET")
WECHAT_AUTHOR = os.getenv("WECHAT_AUTHOR", "猫哥")

API_BASE = "https://api.weixin.qq.com/cgi-bin"
TOKEN_CACHE_FILE = Path(__file__).resolve().parent / ".wechat_token_cache.json"


# ===== 固定模板 =====

# 头部：引导关注
WECHAT_HEADER_HTML = (
    '<p style="text-align:center;margin:0 0 8px;padding:0;color:#8b8378;font-size:13px;line-height:1.5;letter-spacing:0.04em;">△△微信关注"<strong style="color:#306998;font-weight:700;">Python猫</strong>"，回复"<strong style="color:#d4a017;font-weight:700;">1</strong>"领取电子书</p>'
    '<section style="margin:0 0 20px;padding:12px 16px 12px 20px;border-left:3px solid #306998;background:rgba(48,105,152,0.04);">'
    '<p style="color:#777777;font-size:15px;line-height:1.85;letter-spacing:0.04em;margin:4px 0;padding:0;">这里分享的是 Python 潮流周刊免费开源的往期全文，原文发布于一年前。我们的付费专栏内容在发布一年后会免费开源，不少内容依然值得回看，愿大家读有所获。点击文末"阅读原文"，在网页里查看，体验更佳。</p>'
    '<p style="color:#777777;font-size:15px;line-height:1.85;letter-spacing:0.04em;margin:4px 0;padding:0;">温馨提示：在微信关注 Python猫，发送一个数字"<strong style="color:#d4a017;font-weight:700;">9</strong>"，即可领取 9 折优惠券，订阅专栏可享 15 元优惠。订阅后可查看全部已公开和未公开内容！</p>'
    '<p style="color:#777777;font-size:15px;line-height:1.85;letter-spacing:0.04em;margin:4px 0;padding:0;">关注 Python猫后，发一个数字"<strong style="color:#d4a017;font-weight:700;">1</strong>"，可免费领取已开源的往季周刊精华合集。</p>'
    '</section>'
    '<mp-common-miniprogram class="weapp_display_element js_weapp_display_element js_wx_tap_highlight" data-pluginname="insertminiprogram" data-miniprogram-path="pages/webpage/webpage?url=https%3A%2F%2Fxiaobot.net%2Fp%2Fpython_weekly%3Frefer%3D2fc438e2-33fe-44bd-aa2f-ae7d8e782dea%26name%3DPython%25E6%25BD%25AE%25E6%25B5%2581%25E5%2591%25A8%25E5%2588%258A%2520%257C%2520%25E6%25AF%258F%25E5%2591%25A8%25E8%25BF%259E%25E8%25BD%25BD%25E4%25B8%25AD" data-miniprogram-nickname="小报童投递" data-miniprogram-avatar="http://mmbiz.qpic.cn/sz_mmbiz_png/THws1QqamVHlzF6S0wcibjQZcDVyvu6PcFbSDMBfoAn4nFpJITwsFOtTvqsGLXsGiajKwGgM53S8Sh14iay9eGwKw/640?wx_fmt=png&amp;wxfrom=200" data-miniprogram-title="进入Python潮流周刊专栏" data-miniprogram-imageurl="http://mmbiz.qpic.cn/sz_mmbiz_jpg/LLRiaS9YfFTN3pZepX7zEhbKE5rpZNj3ov73icpspldANibaEMKDJhzKkhfTtPLpK93cYpPf8MfNAsIibUKgNGVy3A/0?wx_fmt=jpeg" data-miniprogram-type="card" data-miniprogram-servicetype="0" data-miniprogram-appid="wx783e6b31ada3e12b" data-miniprogram-applink="#小程序://小报童/2RNWfkYOiJnImPB" data-miniprogram-imageurlback="https%3A%2F%2Fmmbiz.qpic.cn%2Fsz_mmbiz_png%2FLLRiaS9YfFTN3pZepX7zEhbKE5rpZNj3oTS48tB9ESDUhEj42efgmlWWJA247DKLzlFL0kPoAyIg6uyiawvb5xnA%2F0%3Fwx_fmt%3Dpng" data-miniprogram-cropperinfo="%7B%22c%22%3A%7B%22x%22%3A0%2C%22y%22%3A79%2C%22x2%22%3A117%2C%22y2%22%3A172.6%2C%22w%22%3A117%2C%22h%22%3A93.6%7D%7D"></mp-common-miniprogram>'
)

# 分割图标
WECHAT_DIVIDER_HTML = (
    '<p style="text-align:center;margin:2em 0 1em;">'
    '<img src="https://mmbiz.qpic.cn/mmbiz/cZV2hRpuAPiaJQXWGyC9wrUzIicibgXayrgibTYarT3A1yzttbtaO0JlV21wMqroGYT3QtPq2C7HMYsvicSB2p7dTBg/640?wx_fmt=gif&amp;tp=webp&amp;wxfrom=5&amp;wx_lazy=1#imgIndex=3" style="width:auto;height:auto;max-width:100%;display:inline-block;vertical-align:middle;margin:0 4px;" alt="divider">'
    '<img src="https://mmbiz.qpic.cn/mmbiz/cZV2hRpuAPiaJQXWGyC9wrUzIicibgXayrgibTYarT3A1yzttbtaO0JlV21wMqroGYT3QtPq2C7HMYsvicSB2p7dTBg/640?wx_fmt=gif&amp;tp=webp&amp;wxfrom=5&amp;wx_lazy=1#imgIndex=3" style="width:auto;height:auto;max-width:100%;display:inline-block;vertical-align:middle;margin:0 4px;" alt="divider">'
    '</p>'
)

# 尾部：推广
WECHAT_FOOTER_HTML = (
    '<section style="margin-top:0;padding-top:0;">'
    '<p style="color:#333333;font-size:15px;line-height:1.85;letter-spacing:0.04em;margin:0.8em 0;text-align:justify;">如果你正在寻找优质的Python文章和项目，我必须向你推荐🎁Python潮流周刊🎁！</p>'
    '<p style="color:#333333;font-size:15px;line-height:1.85;letter-spacing:0.04em;margin:0.8em 0;text-align:justify;">它精选全网的优秀文章、教程、开源项目、软件工具、播客、视频、热门话题等丰富内容，让你紧跟技术最前沿，获取最新的第一手学习资料！</p>'
    '<p style="color:#333333;font-size:15px;line-height:1.85;letter-spacing:0.04em;margin:0.8em 0;text-align:justify;">欢迎点击下方图片，了解这份全世界知识密度最高、知识广度最大的 Python 技术周刊。</p>'
    '</section>'
    '<p style="margin-bottom:0;letter-spacing:0.578px;text-align:center;">'
    '<a href="http://mp.weixin.qq.com/s?__biz=MzUyOTk2MTcwNg==&amp;mid=2247499711&amp;idx=1&amp;sn=3dc40c2b7b1217fe10a30fc8204072a7&amp;chksm=fa5bb83acd2c312c6b5504314c75218abb8278ae9b6942322ae3d140dc3a40afaf38cddbfe29&amp;scene=21#wechat_redirect" imgurl="https://mmbiz.qpic.cn/sz_mmbiz_png/LLRiaS9YfFTNBL4qUj4SJ2UJP9qDvwVajLJGMQrqibt2s57j5Snj2jHnPrKBa2VEPpxmONYickz8tg1D5pvMQiajBA/640?wx_fmt=png&amp;from=appmsg" linktype="image" tab="innerlink" data-itemshowtype="0" target="_blank" data-linktype="1">'
    '<img src="https://mmbiz.qpic.cn/sz_mmbiz_png/LLRiaS9YfFTNBL4qUj4SJ2UJP9qDvwVajLJGMQrqibt2s57j5Snj2jHnPrKBa2VEPpxmONYickz8tg1D5pvMQiajBA/640?wx_fmt=png&amp;from=appmsg" style="width:100%;max-width:677px;height:auto;display:block;margin:0 auto;" alt="Python潮流周刊">'
    '</a>'
    '</p>'
)


def build_copyright_html(orig_author: str, translator: str, orig_title: str, source_url: str) -> str:
    """生成版权信息 HTML"""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = []
    if orig_author:
        lines.append(f'作者：{orig_author}')
    if translator:
        lines.append(f'译者：{translator}')
    if orig_title and source_url:
        lines.append(f'英文：<a href="{source_url}">{orig_title}</a>')
    elif orig_title:
        lines.append(f'英文：{orig_title}')
    lines.append(f'声明：本翻译是出于交流学习的目的，为便于阅读，部分内容略有改动。转载请保留作者信息。')
    lines.append(f'翻译日期：{today}')

    items = ''.join(
        f'<p style="margin:0.2em 0;color:#888888;font-size:14px;line-height:1.6;">{line}</p>'
        for line in lines
    )
    return (
        f'<section style="margin:1.5em 0 0.5em;padding:12px 16px;background:#f9f9f9;border-radius:4px;">'
        f'{items}'
        f'</section>'
    )


# ===== Token 管理 =====
def get_access_token():
    if not WECHAT_APP_ID or not WECHAT_APP_SECRET:
        print("❌ 请在 resources/.env 中设置 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
        sys.exit(1)
    if TOKEN_CACHE_FILE.exists():
        try:
            cache = json.loads(TOKEN_CACHE_FILE.read_text())
            if cache.get("expires_at", 0) > time.time() + 300:
                return cache["access_token"]
        except (json.JSONDecodeError, KeyError):
            pass
    url = f"{API_BASE}/token"
    params = {"grant_type": "client_credential", "appid": WECHAT_APP_ID, "secret": WECHAT_APP_SECRET}
    resp = httpx.get(url, params=params, timeout=15)
    data = resp.json()
    if "access_token" not in data:
        print(f"❌ 获取 access_token 失败: {data}")
        sys.exit(1)
    cache = {"access_token": data["access_token"], "expires_at": time.time() + data.get("expires_in", 7200)}
    TOKEN_CACHE_FILE.write_text(json.dumps(cache))
    return data["access_token"]


# ===== 图片上传 =====
def upload_image(image_url, token):
    print(f"  ⬇ {image_url[:70]}...")
    try:
        img_resp = httpx.get(image_url, follow_redirects=True, timeout=30)
        img_resp.raise_for_status()
        img_data = img_resp.content
    except Exception as e:
        print(f"    ⚠️ 下载失败: {e}")
        return "", ""

    ct = img_resp.headers.get("content-type", "")
    if "png" in ct or image_url.lower().endswith(".png"):
        ext = "png"
    elif "gif" in ct or image_url.lower().endswith(".gif"):
        ext = "gif"
    else:
        ext = "jpg"

    upload_url = f"{API_BASE}/material/add_material?access_token={token}&type=image"
    files = {"media": (f"image.{ext}", img_data, f"image/{ext}")}
    try:
        resp = httpx.post(upload_url, files=files, timeout=60)
        result = resp.json()
    except Exception as e:
        print(f"    ⚠️ 上传失败: {e}")
        return "", ""

    if "media_id" in result:
        return result["media_id"], result.get("url", "")
    else:
        print(f"    ⚠️ 上传异常: {result}")
        return "", ""


# ===== HTML 转换与后处理 =====
def _inline_pygments_css(html: str) -> str:
    formatter = HtmlFormatter(style="friendly")
    full_css = formatter.get_style_defs(".highlight")
    class_styles = {}
    for m in re.finditer(r'(?:\.highlight\s+)?\.(\w+)\s*\{([^}]+)\}', full_css):
        cls, styles = m.group(1), m.group(2).strip()
        if cls not in class_styles:
            class_styles[cls] = styles
    if not class_styles:
        return html
    for cls, style in class_styles.items():
        html = re.sub(rf'class="({cls})"(?!\s+style=)', rf'class="\1" style="{style}"', html)
        html = re.sub(rf'class="([^"]*\s)({cls})(\s[^"]*)"(?!\s+style=)',
                      rf'class="\1\2\3" style="{style}"', html)
    return html


def clean_wechat_html(html: str) -> str:
    """去除标签间空白（保留 <pre> 内部格式）"""
    pre_blocks = []
    def save_pre(m):
        pre_blocks.append(m.group(0))
        return f"__PRE_BLOCK_{len(pre_blocks) - 1}__"
    html = re.sub(r'<pre[^>]*>.*?</pre>', save_pre, html, flags=re.DOTALL)

    # 去除所有标签间的换行和缩进
    html = re.sub(r'>\s+<', '><', html)

    # 减小顶部 padding
    html = html.replace('padding: 16px;', 'padding: 0 16px 16px 16px;')

    # 移除空 <p>
    html = re.sub(r'<p[^>]*>\s*</p>', '', html)

    # 恢复 <pre> 内容
    for i, block in enumerate(pre_blocks):
        html = html.replace(f"__PRE_BLOCK_{i}__", block)

    return html


def convert_md_to_wechat_html(md_content: str, theme: str = "minimal") -> str:
    html = inkpress.convert(md_content, theme=theme)
    html = _inline_pygments_css(html)
    html = clean_wechat_html(html)
    return html


def assemble_final_html(wechat_html: str, copyright_html: str) -> str:
    """从 inkpress 输出中提取 body_content，插入头部/版权/分割/尾部"""
    # inkpress 输出: <body...><section...>BODY_CONTENT</section></body>
    container_match = re.search(
        r'(<body[^>]*>\s*<section[^>]*>)(.*?)(</section>\s*</body>)',
        wechat_html, re.DOTALL
    )
    if not container_match:
        print("⚠️ 无法解析 inkpress 输出结构，使用原始 HTML")
        return wechat_html

    body_prefix = wechat_html[:container_match.start(2)]
    body_content = container_match.group(2)
    body_suffix = wechat_html[container_match.end(2):]

    # 在开头插入头部
    body_content = WECHAT_HEADER_HTML + body_content

    # 在译者话之后插入版权信息（找到第一个 H2 或 <h2 标签之前）
    # 译者话段落以 *—— 译者* 结尾，之后紧跟正文标题
    h2_match = re.search(r'<h[23]\s', body_content)
    if h2_match and copyright_html:
        body_content = body_content[:h2_match.start()] + copyright_html + body_content[h2_match.start():]

    # 在末尾插入分割图标 + 推广
    body_content += WECHAT_DIVIDER_HTML + WECHAT_FOOTER_HTML

    # 重新拼接，并去除 body→section 间空白
    final_html = body_prefix + body_content + body_suffix
    final_html = re.sub(r'>\s+<', '><', final_html)

    return final_html


# ===== 文章信息提取 =====
def extract_article_info(md_content: str, filepath: Path) -> dict:
    lines = md_content.split("\n")
    title = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped.replace("# ", "").strip()
            break
    if not title:
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## "):
                title = stripped.replace("## ", "").strip()
                break
    if not title:
        title = filepath.stem

    digest = ""
    found_title = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not found_title:
            found_title = True
            continue
        if not found_title:
            continue
        if not stripped or stripped.startswith("#") or stripped.startswith("!["):
            continue
        if stripped.startswith("<") and stripped.endswith(">"):
            continue
        digest = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)
        digest = re.sub(r"\*\*([^*]+)\*\*", r"\1", digest)
        digest = re.sub(r"<[^>]+>", "", digest)
        digest = re.sub(r"[#*>_`~]", "", digest)
        if digest:
            if len(digest) > 120:
                digest = digest[:117] + "..."
            break

    cover_url = ""
    img_matches = re.findall(r"!\[.*?\]\(([^)]+)\)", md_content)
    if img_matches:
        cover_url = img_matches[0]

    return {"title": title, "digest": digest, "cover_url": cover_url}


def extract_image_urls(md_content: str) -> list:
    return re.findall(r"!\[.*?\]\(([^)]+)\)", md_content)


# ===== WeChat API =====
def create_draft(token, title, content_html, cover_media_id="", digest="", author="", source_url=""):
    url = f"{API_BASE}/draft/add?access_token={token}"
    article = {
        "title": title,
        "content": content_html,
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }
    if cover_media_id:
        article["thumb_media_id"] = cover_media_id
    if digest:
        article["digest"] = digest
    if author:
        article["author"] = author
    if source_url:
        article["content_source_url"] = source_url

    resp = httpx.post(url, json={"articles": [article]}, timeout=30)
    result = resp.json()
    if "media_id" in result:
        return result["media_id"]
    else:
        print(f"❌ 创建草稿失败: {result}")
        return ""


# ===== 主流程 =====
def main():
    parser = argparse.ArgumentParser(description="翻译文章发布到微信公众号草稿箱")
    parser.add_argument("markdown_file", help="Markdown 文件路径")
    parser.add_argument("--title", default="", help="文章标题（由 API 设置，不出现在正文）")
    parser.add_argument("--author", default=WECHAT_AUTHOR, help=f"公众号作者名 (默认: {WECHAT_AUTHOR})")
    parser.add_argument("--source-url", default="", help="原文链接（文末阅读原文）")
    parser.add_argument("--digest", default="", help="摘要（默认自动提取）")
    parser.add_argument("--theme", default="minimal", help="inkpress 主题 (默认: minimal)")
    parser.add_argument("--skip-image-upload", action="store_true", help="跳过图片上传")
    # 版权信息
    parser.add_argument("--orig-author", default="", help="原文作者")
    parser.add_argument("--orig-title", default="", help="原文标题")
    parser.add_argument("--translator", default="", help="译者署名（默认用 --author）")
    parser.set_defaults(draft_only=True)

    args = parser.parse_args()
    filepath = Path(args.markdown_file)
    if not filepath.exists():
        print(f"❌ 文件不存在: {filepath}")
        sys.exit(1)

    md_content = filepath.read_text(encoding="utf-8")

    print("=" * 60)
    print("📡 翻译文章发布到微信草稿箱")
    print("=" * 60)

    # 1. Token
    print("\n[1/5] 获取 access_token...")
    token = get_access_token()
    print(f"  ✓ token: {token[:16]}...")

    # 2. 提取信息
    print("\n[2/5] 提取文章信息...")
    info = extract_article_info(md_content, filepath)
    if args.title:
        info["title"] = args.title
    if args.digest:
        info["digest"] = args.digest
    translator = args.translator or args.author
    print(f"  标题: {info['title']}")
    print(f"  摘要: {info['digest'][:60] if info['digest'] else '(未提取到)'}")
    if info["cover_url"]:
        print(f"  封面图: {info['cover_url'][:80]}")

    # 3. 上传图片
    image_map = {}
    cover_media_id = ""
    cover_wechat_url = ""

    print("\n[3/5] 处理封面图和文章图片...")
    if info["cover_url"] and not args.skip_image_upload:
        print(f"  上传封面图...")
        cover_media_id, cover_wechat_url = upload_image(info["cover_url"], token)
        if cover_media_id:
            image_map[info["cover_url"]] = cover_wechat_url
            print(f"  ✓ cover media_id: {cover_media_id[:16]}...")

    if not cover_media_id:
        print("❌ 必须有封面图！请在文章中插入至少一张图片")
        sys.exit(1)

    if not args.skip_image_upload:
        image_urls = extract_image_urls(md_content)
        if image_urls:
            print(f"  共 {len(image_urls)} 张图片")
            for i, img_url in enumerate(image_urls, 1):
                if img_url in image_map:
                    print(f"  [{i}/{len(image_urls)}] 跳过（已作为封面上传）")
                    continue
                print(f"  [{i}/{len(image_urls)}] ", end="")
                mid, wurl = upload_image(img_url, token)
                if mid:
                    image_map[img_url] = wurl
                time.sleep(0.3)

    # 4. Markdown → HTML → 拼接头尾
    print(f"\n[4/5] 转换 Markdown → 微信 HTML（主题: {args.theme}）...")
    wechat_html = convert_md_to_wechat_html(md_content, theme=args.theme)

    # 替换图片 URL
    replaced = 0
    for orig_url, wx_url in image_map.items():
        if wx_url:
            wechat_html = wechat_html.replace(orig_url, wx_url)
            replaced += 1
    print(f"  ✓ 替换了 {replaced} 张图片为微信 CDN URL")

    # 生成版权信息并拼接头尾
    copyright_html = build_copyright_html(
        orig_author=args.orig_author,
        translator=translator,
        orig_title=args.orig_title,
        source_url=args.source_url,
    )
    final_html = assemble_final_html(wechat_html, copyright_html)
    print(f"  HTML 长度: {len(final_html)} 字符")

    # 保存 HTML
    html_file = filepath.with_suffix(".wechat.html")
    html_file.write_text(final_html, encoding="utf-8")
    print(f"  HTML 已保存到: {html_file}")

    # 5. 创建草稿
    print(f"\n[5/5] 创建草稿...")
    if args.source_url:
        print(f"  原文链接: {args.source_url}")

    draft_media_id = create_draft(
        token=token,
        title=info["title"],
        content_html=final_html,
        cover_media_id=cover_media_id,
        digest=info["digest"],
        author=args.author,
        source_url=args.source_url,
    )

    if draft_media_id:
        print(f"  ✓ 草稿创建成功！media_id: {draft_media_id}")
    else:
        print("❌ 草稿创建失败")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ 完成！请在公众号后台检查草稿")
    print("=" * 60)


if __name__ == "__main__":
    main()
