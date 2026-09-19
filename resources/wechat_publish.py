#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""微信公众号文章发布脚本。

用法：
  python3 resources/wechat_publish.py <markdown_file> [选项]

功能：
  1. 读取周刊 Markdown 文件
  2. 提取标题、摘要、封面图
  3. 上传图片到微信素材库，替换文章中的图片 URL
  4. 将 Markdown 转换为微信兼容的 HTML（内联样式）
  5. 通过微信 API 创建草稿
  6. 可选：发布草稿

示例：
  python3 resources/wechat_publish.py docs/2026-06-07-weekly.md
  python3 resources/wechat_publish.py docs/2026-06-07-weekly.md --draft-only
  python3 resources/wechat_publish.py docs/2026-06-07-weekly.md --publish
"""

import os
import re
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

import httpx
from dotenv import load_dotenv

# inkpress: Markdown → 微信兼容 HTML（内联样式，25 种主题）
import inkpress

# Pygments: 代码语法高亮 → 内联样式
from pygments.formatters import HtmlFormatter

# ===== 加载配置 =====
load_dotenv(Path(__file__).resolve().parent / ".env")

WECHAT_APP_ID = os.getenv("WECHAT_APP_ID")
WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET")
WECHAT_AUTHOR = os.getenv("WECHAT_AUTHOR", "猫哥")

API_BASE = "https://api.weixin.qq.com/cgi-bin"
TOKEN_CACHE_FILE = Path(__file__).resolve().parent / ".wechat_token_cache.json"

# ===== 微信固定模板（与 republish_full_weekly.py 一致）=====

# 全文版头部模板：引导关注 + "往期全文"说明 + 小程序卡片（用于 republish_full_weekly）
WECHAT_HEADER_FULL_HTML = (
    '<p style="text-align:center;margin:0 0 8px;padding:0;color:#8b8378;font-family:\'PingFang SC\',-apple-system,BlinkMacSystemFont,\'Helvetica Neue\',sans-serif;font-size:13px;line-height:1.5;letter-spacing:0.04em;">△△微信关注"<strong style="color:#306998;font-weight:700;">Python猫</strong>"，回复"<strong style="color:#d4a017;font-weight:700;">1</strong>"领取电子书</p>'
    '<section style="margin:0 0 20px;padding:12px 16px 12px 20px;border-left:3px solid #306998;background:rgba(48,105,152,0.04);">'
    '<p style="color:#777777;font-family:\'PingFang SC\',-apple-system,BlinkMacSystemFont,\'Helvetica Neue\',sans-serif;font-size:15px;line-height:1.85;letter-spacing:0.04em;margin:4px 0;padding:0;">这里分享的是 Python 潮流周刊免费开源的往期全文，原文发布于一年前。我们的付费专栏内容在发布一年后会免费开源，不少内容依然值得回看，愿大家读有所获。点击文末"阅读原文"，在网页里查看，体验更佳。</p>'
    '<p style="color:#777777;font-family:\'PingFang SC\',-apple-system,BlinkMacSystemFont,\'Helvetica Neue\',sans-serif;font-size:15px;line-height:1.85;letter-spacing:0.04em;margin:4px 0;padding:0;">温馨提示：在微信关注 Python猫，发送一个数字"<strong style="color:#d4a017;font-weight:700;">9</strong>"，即可领取 9 折优惠券，订阅专栏可享 15 元优惠。订阅后可查看全部已公开和未公开内容！</p>'
    '<p style="color:#777777;font-family:\'PingFang SC\',-apple-system,BlinkMacSystemFont,\'Helvetica Neue\',sans-serif;font-size:15px;line-height:1.85;letter-spacing:0.04em;margin:4px 0;padding:0;">关注 Python猫后，发一个数字"<strong style="color:#d4a017;font-weight:700;">1</strong>"，可免费领取已开源的往季周刊精华合集。</p>'
    '</section>'
    '<mp-common-miniprogram class="weapp_display_element js_weapp_display_element js_wx_tap_highlight" data-pluginname="insertminiprogram" data-miniprogram-path="pages/webpage/webpage?url=https%3A%2F%2Fxiaobot.net%2Fp%2Fpython_weekly%3Frefer%3D2fc438e2-33fe-44bd-aa2f-ae7d8e782dea%26name%3DPython%25E6%25BD%25AE%25E6%25B5%2581%25E5%2591%25A8%25E5%2588%258A%2520%257C%2520%25E6%25AF%258F%25E5%2591%25A8%25E8%25BF%259E%25E8%25BD%25BD%25E4%25B8%25AD" data-miniprogram-nickname="小报童投递" data-miniprogram-avatar="http://mmbiz.qpic.cn/sz_mmbiz_png/THws1QqamVHlzF6S0wcibjQZcDVyvu6PcFbSDMBfoAn4nFpJITwsFOtTvqsGLXsGiajKwGgM53S8Sh14iay9eGwKw/640?wx_fmt=png&amp;wxfrom=200" data-miniprogram-title="进入Python潮流周刊专栏" data-miniprogram-imageurl="http://mmbiz.qpic.cn/sz_mmbiz_jpg/LLRiaS9YfFTN3pZepX7zEhbKE5rpZNj3ov73icpspldANibaEMKDJhzKkhfTtPLpK93cYpPf8MfNAsIibUKgNGVy3A/0?wx_fmt=jpeg" data-miniprogram-type="card" data-miniprogram-servicetype="0" data-miniprogram-appid="wx783e6b31ada3e12b" data-miniprogram-applink="#小程序://小报童/2RNWfkYOiJnImPB" data-miniprogram-imageurlback="https%3A%2F%2Fmmbiz.qpic.cn%2Fsz_mmbiz_png%2FLLRiaS9YfFTN3pZepX7zEhbKE5rpZNj3oTS48tB9ESDUhEj42efgmlWWJA247DKLzlFL0kPoAyIg6uyiawvb5xnA%2F0%3Fwx_fmt%3Dpng" data-miniprogram-cropperinfo="%7B%22c%22%3A%7B%22x%22%3A0%2C%22y%22%3A79%2C%22x2%22%3A117%2C%22y2%22%3A172.6%2C%22w%22%3A117%2C%22h%22%3A93.6%7D%7D"></mp-common-miniprogram>'
)

# 简化版头部模板：仅保留顶部引导关注行 + 小程序卡片（无"往期全文"说明）
WECHAT_HEADER_SIMPLIFIED_HTML = (
    '<p style="text-align:center;margin:0 0 8px;padding:0;color:#8b8378;font-family:\'PingFang SC\',-apple-system,BlinkMacSystemFont,\'Helvetica Neue\',sans-serif;font-size:13px;line-height:1.5;letter-spacing:0.04em;">△△微信关注"<strong style="color:#306998;font-weight:700;">Python猫</strong>"，回复"<strong style="color:#d4a017;font-weight:700;">1</strong>"领取电子书</p>'
    '<mp-common-miniprogram class="weapp_display_element js_weapp_display_element js_wx_tap_highlight" data-pluginname="insertminiprogram" data-miniprogram-path="pages/webpage/webpage?url=https%3A%2F%2Fxiaobot.net%2Fp%2Fpython_weekly%3Frefer%3D2fc438e2-33fe-44bd-aa2f-ae7d8e782dea%26name%3DPython%25E6%25BD%25AE%25E6%25B5%2581%25E5%2591%25A8%25E5%2588%258A%2520%257C%2520%25E6%25AF%258F%25E5%2591%25A8%25E8%25BF%259E%25E8%25BD%25BD%25E4%25B8%25AD" data-miniprogram-nickname="小报童投递" data-miniprogram-avatar="http://mmbiz.qpic.cn/sz_mmbiz_png/THws1QqamVHlzF6S0wcibjQZcDVyvu6PcFbSDMBfoAn4nFpJITwsFOtTvqsGLXsGiajKwGgM53S8Sh14iay9eGwKw/640?wx_fmt=png&amp;wxfrom=200" data-miniprogram-title="进入Python潮流周刊专栏" data-miniprogram-imageurl="http://mmbiz.qpic.cn/sz_mmbiz_jpg/LLRiaS9YfFTN3pZepX7zEhbKE5rpZNj3ov73icpspldANibaEMKDJhzKkhfTtPLpK93cYpPf8MfNAsIibUKgNGVy3A/0?wx_fmt=jpeg" data-miniprogram-type="card" data-miniprogram-servicetype="0" data-miniprogram-appid="wx783e6b31ada3e12b" data-miniprogram-applink="#小程序://小报童/2RNWfkYOiJnImPB" data-miniprogram-imageurlback="https%3A%2F%2Fmmbiz.qpic.cn%2Fsz_mmbiz_png%2FLLRiaS9YfFTN3pZepX7zEhbKE5rpZNj3oTS48tB9ESDUhEj42efgmlWWJA247DKLzlFL0kPoAyIg6uyiawvb5xnA%2F0%3Fwx_fmt%3Dpng" data-miniprogram-cropperinfo="%7B%22c%22%3A%7B%22x%22%3A0%2C%22y%22%3A79%2C%22x2%22%3A117%2C%22y2%22%3A172.6%2C%22w%22%3A117%2C%22h%22%3A93.6%7D%7D"></mp-common-miniprogram>'
)

# 向后兼容别名
WECHAT_HEADER_HTML = WECHAT_HEADER_FULL_HTML

WECHAT_FOOTER_HTML = (
    '<section style="margin-top:0;padding-top:0;">'
    '<p style="color:#333333;font-family:\'PingFang SC\',-apple-system,BlinkMacSystemFont,\'Helvetica Neue\',sans-serif;font-size:15px;line-height:1.85;letter-spacing:0.04em;margin:0.8em 0;text-align:justify;">如果你正在寻找优质的Python文章和项目，我必须向你推荐🎁Python潮流周刊🎁！</p>'
    '<p style="color:#333333;font-family:\'PingFang SC\',-apple-system,BlinkMacSystemFont,\'Helvetica Neue\',sans-serif;font-size:15px;line-height:1.85;letter-spacing:0.04em;margin:0.8em 0;text-align:justify;">它精选全网的优秀文章、教程、开源项目、软件工具、播客、视频、热门话题等丰富内容，让你紧跟技术最前沿，获取最新的第一手学习资料！</p>'
    '<p style="color:#333333;font-family:\'PingFang SC\',-apple-system,BlinkMacSystemFont,\'Helvetica Neue\',sans-serif;font-size:15px;line-height:1.85;letter-spacing:0.04em;margin:0.8em 0;text-align:justify;">欢迎点击下方图片，了解这份全世界知识密度最高、知识广度最大的 Python 技术周刊。</p>'
    '</section>'
    '<p style="margin-bottom:0;letter-spacing:0.578px;text-align:center;">'
    '<a href="http://mp.weixin.qq.com/s?__biz=MzUyOTk2MTcwNg==&amp;mid=2247499711&amp;idx=1&amp;sn=3dc40c2b7b1217fe10a30fc8204072a7&amp;chksm=fa5bb83acd2c312c6b5504314c75218abb8278ae9b6942322ae3d140dc3a40afaf38cddbfe29&amp;scene=21#wechat_redirect" imgurl="https://mmbiz.qpic.cn/sz_mmbiz_png/LLRiaS9YfFTNBL4qUj4SJ2UJP9qDvwVajLJGMQrqibt2s57j5Snj2jHnPrKBa2VEPpxmONYickz8tg1D5pvMQiajBA/640?wx_fmt=png&amp;from=appmsg" linktype="image" tab="innerlink" data-itemshowtype="0" target="_blank" data-linktype="1">'
    '<img src="https://mmbiz.qpic.cn/sz_mmbiz_png/LLRiaS9YfFTNBL4qUj4SJ2UJP9qDvwVajLJGMQrqibt2s57j5Snj2jHnPrKBa2VEPpxmONYickz8tg1D5pvMQiajBA/640?wx_fmt=png&amp;from=appmsg" style="width:100%;max-width:677px;height:auto;display:block;margin:0 auto;" alt="Python潮流周刊">'
    '</a>'
    '</p>'
)

WECHAT_DIVIDER_HTML = (
    '<p style="text-align:center;margin:2em 0 1em;">'
    '<img src="https://mmbiz.qpic.cn/mmbiz/cZV2hRpuAPiaJQXWGyC9wrUzIicibgXayrgibTYarT3A1yzttbtaO0JlV21wMqroGYT3QtPq2C7HMYsvicSB2p7dTBg/640?wx_fmt=gif&amp;tp=webp&amp;wxfrom=5&amp;wx_lazy=1#imgIndex=3" style="width:auto;height:auto;max-width:100%;display:inline-block;vertical-align:middle;margin:0 4px;" alt="divider">'
    '<img src="https://mmbiz.qpic.cn/mmbiz/cZV2hRpuAPiaJQXWGyC9wrUzIicibgXayrgibTYarT3A1yzttbtaO0JlV21wMqroGYT3QtPq2C7HMYsvicSB2p7dTBg/640?wx_fmt=gif&amp;tp=webp&amp;wxfrom=5&amp;wx_lazy=1#imgIndex=3" style="width:auto;height:auto;max-width:100%;display:inline-block;vertical-align:middle;margin:0 4px;" alt="divider">'
    '</p>'
)


# ===== Token 管理 =====

def get_access_token() -> str:
    """获取微信 access_token，优先使用缓存"""
    if not WECHAT_APP_ID or not WECHAT_APP_SECRET:
        print("❌ 请在 resources/.env 中设置 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
        print("   获取方式: developers.weixin.qq.com → 我的业务与服务 → 公众号 → 开发密钥")
        sys.exit(1)

    # 检查缓存
    if TOKEN_CACHE_FILE.exists():
        try:
            cache = json.loads(TOKEN_CACHE_FILE.read_text())
            if cache.get("expires_at", 0) > time.time() + 300:  # 5分钟缓冲
                return cache["access_token"]
        except (json.JSONDecodeError, KeyError):
            pass

    # 获取新 token
    url = f"{API_BASE}/token"
    params = {
        "grant_type": "client_credential",
        "appid": WECHAT_APP_ID,
        "secret": WECHAT_APP_SECRET,
    }
    resp = httpx.get(url, params=params, timeout=15)
    data = resp.json()

    if "access_token" not in data:
        print(f"❌ 获取 access_token 失败: {data}")
        sys.exit(1)

    # 缓存 token
    cache = {
        "access_token": data["access_token"],
        "expires_at": time.time() + data.get("expires_in", 7200),
    }
    TOKEN_CACHE_FILE.write_text(json.dumps(cache))

    return data["access_token"]


# ===== 图片上传 =====

def upload_image_to_wechat(image_url: str, token: str) -> tuple[str, str]:
    """上传单张图片到微信永久素材库（通过 URL 下载），返回 (media_id, wechat_url)。

    微信的永久图片素材返回的 URL 才是能在文章里直接用的。
    """
    # 1. 下载图片
    print(f"  ⬇ 下载图片: {image_url[:80]}")
    try:
        img_resp = httpx.get(image_url, follow_redirects=True, timeout=30)
        img_resp.raise_for_status()
        img_data = img_resp.content
    except Exception as e:
        print(f"    ⚠️ 下载失败: {e}")
        return "", ""

    # 2. 判断文件类型并转换：GIF 保留原样，其他格式统一转 JPEG
    #    微信会将 PNG 转为 RGBA 格式，透明/白色边缘渲染异常（黑边），因此强制转 JPEG
    is_gif = img_data.startswith(b"GIF8")
    if not is_gif:
        try:
            from PIL import Image
            import io as _io
            img = Image.open(_io.BytesIO(img_data))
            if img.mode in ("RGBA", "LA", "PA", "P"):
                # 透明/调色板 → RGB 白底
                rgb = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                rgb.paste(img, (0, 0), img if img.mode == "RGBA" else None)
                img = rgb
            elif img.mode != "RGB":
                img = img.convert("RGB")
            jpeg_buf = _io.BytesIO()
            img.save(jpeg_buf, format="JPEG", quality=92)
            img_data = jpeg_buf.getvalue()
            ext = "jpg"
        except Exception:
            # PIL 转换失败，尝试用 macOS sips 兜底
            ext = "jpg"
            try:
                import subprocess, tempfile, os as _os
                with tempfile.NamedTemporaryFile(suffix=".img", delete=False) as tmp_in:
                    tmp_in.write(img_data)
                    tmp_in_path = tmp_in.name
                tmp_out_path = tmp_in_path + ".jpg"
                subprocess.run(
                    ["sips", "-s", "format", "jpeg", tmp_in_path, "--out", tmp_out_path],
                    check=True, capture_output=True, timeout=30,
                )
                with open(tmp_out_path, "rb") as f:
                    img_data = f.read()
                _os.unlink(tmp_in_path)
                _os.unlink(tmp_out_path)
            except Exception:
                pass  # 彻底失败，保持原样
    else:
        ext = "gif"

    # 3. 上传到微信素材库
    upload_url = f"{API_BASE}/material/add_material?access_token={token}&type=image"
    files = {"media": (f"image.{ext}", img_data, f"image/{ext}")}
    try:
        resp = httpx.post(upload_url, files=files, timeout=60)
        result = resp.json()
    except Exception as e:
        print(f"    ⚠️ 上传失败: {e}")
        return "", ""

    if "media_id" in result:
        media_id = result["media_id"]
        wechat_url = result.get("url", "")
        print(f"    ✓ media_id: {media_id[:16]}..., url: {wechat_url[:60]}")
        return media_id, wechat_url
    else:
        print(f"    ⚠️ 上传返回异常: {result}")
        return "", ""


def upload_cover_file(filepath: Path, token: str) -> str:
    """上传本地封面图到微信素材库，返回 media_id

    非 JPEG 图片会转为 JPEG 后上传，避免微信 PNG→RGBA 转换导致黑边。
    """
    if not filepath.exists():
        print(f"  ⚠️ 封面图不存在: {filepath}")
        return ""

    raw_data = filepath.read_bytes()

    # 转换 PNG/其他格式为 JPEG（GIF 除外）
    if not raw_data.startswith(b"GIF8") and not raw_data.startswith(b"\xff\xd8"):
        try:
            from PIL import Image
            import io as _io
            img = Image.open(_io.BytesIO(raw_data))
            if img.mode in ("RGBA", "LA", "PA", "P"):
                rgb = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                rgb.paste(img, (0, 0), img if img.mode == "RGBA" else None)
                img = rgb
            elif img.mode != "RGB":
                img = img.convert("RGB")
            jpeg_buf = _io.BytesIO()
            img.save(jpeg_buf, format="JPEG", quality=92)
            raw_data = jpeg_buf.getvalue()
            ext = "jpg"
        except Exception:
            ext = "jpg"
    elif raw_data.startswith(b"\xff\xd8"):
        ext = "jpg"
    else:
        ext = "gif"

    print(f"  上传封面: {filepath} → JPEG ({len(raw_data) / 1024:.0f}KB)")

    upload_url = f"{API_BASE}/material/add_material?access_token={token}&type=image"
    files = {"media": (f"cover.{ext}", raw_data, f"image/{ext}")}
    try:
        resp = httpx.post(upload_url, files=files, timeout=60)
        result = resp.json()
    except Exception as e:
        print(f"    ⚠️ 上传失败: {e}")
        return ""

    if "media_id" in result:
        media_id = result["media_id"]
        print(f"    ✓ cover media_id: {media_id[:16]}...")
        return media_id
    else:
        print(f"    ⚠️ 上传返回异常: {result}")
        return ""


def replace_images_in_html(html: str, image_map: dict[str, str]) -> str:
    """将 HTML 中的原始图片 URL 替换为微信 CDN URL"""
    for original_url, wechat_url in image_map.items():
        if wechat_url:
            html = html.replace(original_url, wechat_url)
    return html


# ===== Markdown → 微信 HTML（inkpress 主题引擎） =====
# 使用 inkpress 渲染，主题文件: ~/.inkpress/themes/python-weekly.yaml

def _inline_pygments_css(html: str) -> str:
    """将 Pygments 代码高亮的 CSS class 转为内联 style。

    inkpress 使用 Pygments 生成语法高亮 (class-based HTML)。
    微信不支持 <style> 标签，需要将 class 转为内联 style 属性。
    """
    import re as _re
    formatter = HtmlFormatter(style="monokai")
    full_css = formatter.get_style_defs(".highlight")

    class_styles: dict[str, str] = {}
    for match in _re.finditer(r'(?:\.highlight\s+)?\.(\w+)\s*\{([^}]+)\}', full_css):
        cls = match.group(1)
        styles = match.group(2).strip()
        if cls not in class_styles:
            class_styles[cls] = styles

    if not class_styles:
        return html

    for cls, style in class_styles.items():
        # 只替换尚未带 style 的 class（避免重复添加）
        html = _re.sub(
            rf'class="({cls})"(?!\s+style=)',
            rf'class="\1" style="{style}"',
            html,
        )
        html = _re.sub(
            rf'class="([^"]*\s)({cls})(\s[^"]*)"(?!\s+style=)',
            rf'class="\1\2\3" style="{style}"',
            html,
        )

    return html


def convert_md_to_wechat_html(md_content: str, theme: str = "python-weekly-v2") -> str:
    """用 inkpress 将 Markdown 转为微信兼容 HTML（全内联样式）。

    Args:
        md_content: Markdown 原文
        theme: inkpress 主题名（默认 python-weekly）

    Returns:
        完整 HTML 字符串（可直接用于微信草稿 content 字段）
    """
    # inkpress 渲染：自动应用 YAML 主题 → 全内联样式 HTML
    html = inkpress.convert(md_content, theme=theme)

    # Pygments 代码高亮 class → 内联 style
    html = _inline_pygments_css(html)

    return html


# ===== 文章信息提取 =====

def extract_article_info(md_content: str, filepath: Path) -> dict:
    """从 Markdown 提取文章元信息"""
    lines = md_content.split("\n")

    # 标题：扫描所有行找到第一个 H1 标题
    title = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped.replace("# ", "").strip()
            break
    if not title:
        # 从文件名推断
        stem = filepath.stem  # e.g., "2026-06-07-weekly" or "2025-05-24-weekly-wechat"
        date_part = stem.replace("-weekly-wechat", "").replace("-weekly", "")
        title = f"Python 潮流周刊 | {date_part}"

    # 摘要：取第一段非标题、非 HTML 标签的文字
    digest = ""
    for line in lines[1:]:
        stripped = line.strip()
        # 跳过 HTML 标签行（如头部模板）、标题、图片
        if not stripped or stripped.startswith("#") or stripped.startswith("!["):
            continue
        if stripped.startswith("<") and stripped.endswith(">"):
            continue
        # 清理 markdown 格式和 HTML 标签
        digest = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)
        digest = re.sub(r"\*\*([^*]+)\*\*", r"\1", digest)
        digest = re.sub(r"<[^>]+>", "", digest)  # 去除 HTML 标签
        digest = re.sub(r"[#*>_`~]", "", digest)
        if digest:
            if len(digest) > 120:
                digest = digest[:117] + "..."
            break

    # 封面图：提取文章第一张图片的 URL
    cover_url = ""
    img_matches = re.findall(r"!\[.*?\]\(([^)]+)\)", md_content)
    if img_matches:
        cover_url = img_matches[0]

    return {
        "title": title,
        "digest": digest,
        "cover_url": cover_url,
    }


def extract_image_urls(md_content: str) -> list[str]:
    """提取 Markdown 中所有图片 URL"""
    return re.findall(r"!\[.*?\]\(([^)]+)\)", md_content)


# ===== 创建草稿 =====

def create_draft(
    token: str,
    title: str,
    content_html: str,
    cover_media_id: str = "",
    digest: str = "",
    author: str = "",
    source_url: str = "",
) -> str:
    """创建微信公众号草稿，返回 media_id"""
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

    payload = {"articles": [article]}

    resp = httpx.post(url, json=payload, timeout=30)
    result = resp.json()

    if "media_id" in result:
        return result["media_id"]
    else:
        print(f"❌ 创建草稿失败: {result}")
        return ""


# ===== 发布草稿 =====

def publish_draft(token: str, media_id: str) -> bool:
    """发布草稿"""
    url = f"{API_BASE}/freepublish/submit?access_token={token}"
    payload = {"media_id": media_id}

    resp = httpx.post(url, json=payload, timeout=30)
    result = resp.json()

    if result.get("errcode") == 0:
        publish_id = result.get("publish_id", "")
        print(f"  ✓ 发布成功！publish_id: {publish_id}")
        return True
    else:
        print(f"  ⚠️ 发布失败: {result}")
        return False


# ===== 主流程 =====

def main():
    parser = argparse.ArgumentParser(
        description="微信公众号文章发布工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 resources/wechat_publish.py docs/2026-06-07-weekly.md
  python3 resources/wechat_publish.py docs/2026-06-07-weekly.md --draft-only
  python3 resources/wechat_publish.py docs/2026-06-07-weekly.md --publish
  python3 resources/wechat_publish.py docs/2026-06-07-weekly.md --author "豌豆花"
        """,
    )
    parser.add_argument("markdown_file", help="周刊 Markdown 文件路径")
    parser.add_argument("--draft-only", action="store_true", help="仅保存草稿，不发布")
    parser.add_argument("--publish", action="store_true", help="创建草稿后立即发布")
    parser.add_argument("--author", default=WECHAT_AUTHOR, help=f"作者名 (默认: {WECHAT_AUTHOR})")
    parser.add_argument("--source-url", default="", help="原文链接")
    parser.add_argument("--skip-image-upload", action="store_true", help="跳过图片上传（使用原始URL）")
    parser.add_argument("--cover", default="", help="封面图路径（本地文件，必填）")
    parser.add_argument("--full", action="store_true", help="发布全文版（默认简化版：不声明原创、不开广告、不含原文链接）")
    parser.add_argument("--no-source-url", action="store_true", help="不自动生成原文链接")
    parser.add_argument("--no-digest", action="store_true", help="清空摘要（简化版必用）")
    parser.add_argument("--theme", default="python-weekly-v2", help="inkpress 主题名称（默认: python-weekly-v2）")
    parser.set_defaults(draft_only=True)  # 默认只存草稿，安全第一

    args = parser.parse_args()

    filepath = Path(args.markdown_file)
    if not filepath.exists():
        print(f"❌ 文件不存在: {filepath}")
        sys.exit(1)

    md_content = filepath.read_text(encoding="utf-8")

    # 从文件名推导日期和原文链接
    import re as _re
    date_match = _re.match(r"(\d{4}-\d{2}-\d{2})-weekly\.md$", filepath.name)
    issue_date = date_match.group(1) if date_match else ""
    source_url = args.source_url
    if not source_url and issue_date and not args.no_source_url:
        source_url = f"https://pythoncat.top/posts/{issue_date}-weekly"

    print("=" * 60)
    print("📡 微信公众号文章发布")
    print("=" * 60)

    # 1. 获取 access_token
    print("\n[1/6] 获取 access_token...")
    token = get_access_token()
    print(f"  ✓ token: {token[:16]}...")

    # 2. 提取文章信息
    print("\n[2/6] 提取文章信息...")
    info = extract_article_info(md_content, filepath)
    print(f"  标题: {info['title']}")
    print(f"  摘要: {info['digest'][:60]}...")
    if info["cover_url"]:
        print(f"  封面图: {info['cover_url'][:80]}")

    # 3. 上传封面图
    image_map: dict[str, str] = {}  # original_url → wechat_url
    cover_media_id = ""

    print("\n[3/6] 处理封面图...")
    if args.cover:
        # 用户指定了封面图文件
        cover_media_id = upload_cover_file(Path(args.cover), token)
    elif info["cover_url"] and not args.skip_image_upload:
        # 用文章第一张图做封面
        print(f"  使用文章首图做封面...")
        cover_media_id, _ = upload_image_to_wechat(info["cover_url"], token)
    else:
        print("  ⚠️ 无封面图！")

    if not cover_media_id:
        print("❌ 微信公众号草稿必须有封面图！")
        print("   请用 --cover <图片路径> 指定封面图，或在文章中插入至少一张图片")
        sys.exit(1)

    # 4. 上传文章内图片
    if not args.skip_image_upload:
        print("\n[4/6] 上传文章图片到微信素材库...")
        image_urls = extract_image_urls(md_content)
        if image_urls:
            print(f"  共 {len(image_urls)} 张图片")
            for i, img_url in enumerate(image_urls, 1):
                # 如果这张图就是通过 URL 上传的封面（非本地文件），跳过
                if img_url == info["cover_url"] and cover_media_id and not args.cover:
                    wechat_url = ""  # 用不到 url，上传素材已有
                    image_map[img_url] = wechat_url
                    print(f"  [{i}/{len(image_urls)}] 跳过（已用作封面）")
                    continue
                print(f"  [{i}/{len(image_urls)}]", end="")
                media_id, wechat_url = upload_image_to_wechat(img_url, token)
                if media_id:
                    image_map[img_url] = wechat_url
                time.sleep(0.3)
        else:
            print("  无图片需要上传（纯文字文章）")
    else:
        print("\n[4/6] 跳过文章图片上传 (--skip-image-upload)")

    # 5. Markdown → 微信 HTML
    print(f"\n[5/6] 转换 Markdown → 微信 HTML（主题: {args.theme}）...")
    # 去掉一级标题（微信 title 字段已显示标题，正文不需要重复）
    body_content = re.sub(r'^# .+\n+', '', md_content, count=1)

    if not args.full:
        # 简化版特殊处理：
        # a. 去掉末尾的 "**微信关注 Python猫**：..." 行
        body_content = re.sub(
            r'\n\*\*微信关注 Python猫\*\*[：:]\s*\[?https?://[^\n]+\]?\(https?://[^\n]+\)\s*$',
            '', body_content
        )
        print("  ✓ 简化版：去掉末尾「微信关注 Python猫」")

        # b. 去掉分类标题（**粗体**）里的 markdown 链接
        #    **[🦄文章&教程](url)** → **🦄文章&教程**
        body_content = re.sub(
            r'(\*\*\[)([^\]]+)(\]\([^)]+\)\*\*)',
            r'**\2**', body_content
        )
        print("  ✓ 简化版：去掉分类标题的链接")

        # c. 若链接文字与 URL 相同，只保留文字（避免 url（url）冗余）
        body_content = re.sub(r'\[([^\]]+)\]\(\1\)', r'\1', body_content)
        print("  ✓ 简化版：去掉文字与 URL 相同的冗余链接")

        # d. 将剩余 [text](url) 转为 text（url），保留链接信息（微信会剥离 <a> 标签）
        body_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1（\2）', body_content)
        print("  ✓ 简化版：链接转为 text（url）格式")

    wechat_html = convert_md_to_wechat_html(body_content, theme=args.theme)

    # 替换图片 URL
    if image_map:
        wechat_html = replace_images_in_html(wechat_html, image_map)
        replaced = sum(1 for v in image_map.values() if v)
        print(f"  ✓ 替换了 {replaced} 张图片为微信 CDN URL")

    # 注入微信头部/尾部模板
    container_match = re.search(
        r'(<body[^>]*>\s*<section[^>]*>)(.*?)(</section>\s*</body>)',
        wechat_html, re.DOTALL
    )
    if container_match:
        prefix = wechat_html[:container_match.start(2)]
        body = container_match.group(2)
        suffix = wechat_html[container_match.end(2):]
        # 去除顶部空白
        prefix = prefix.replace('padding: 12px;', 'padding: 0;')
        prefix = prefix.replace('padding: 20px 16px', 'padding: 0 16px 20px 16px')
        prefix = prefix.replace('>\n  <section', '><section')
    else:
        prefix, body, suffix = "", wechat_html, ""

    if not args.full:
        # 简化版：使用精简头部（仅引导关注行 + 小程序卡片，无"往期全文"说明）
        body = WECHAT_HEADER_SIMPLIFIED_HTML + body
        # 左对齐：将 text-align:justify（含可能的空格变体）替换为 text-align:left
        body = re.sub(r'text-align:\s*justify', 'text-align:left', body)
        print("  ✓ 简化版：正文左对齐")
    else:
        # 全文版头部（引导关注 + "往期全文"说明 + 小程序卡片）
        body = WECHAT_HEADER_FULL_HTML + body

    # 尾部模板放在容器内部末尾（微信编辑器保留 linktype="image" 属性）
    body += WECHAT_DIVIDER_HTML + WECHAT_FOOTER_HTML
    wechat_html = prefix + body + suffix
    print(f"  ✓ 已注入微信头部/尾部模板")

    print(f"  HTML 长度: {len(wechat_html)} 字符")

    # 保存 HTML 供检查
    html_file = filepath.with_suffix(".wechat.html")
    html_file.write_text(wechat_html, encoding="utf-8")
    print(f"  HTML 已保存到: {html_file}")

    # 6. 创建草稿 / 发布
    mode_label = "全文版" if args.full else "简化版"
    print(f"\n[6/6] 创建草稿（{mode_label}）...")
    if source_url:
        print(f"  原文链接: {source_url}")

    draft_media_id = create_draft(
        token=token,
        title=info["title"],
        content_html=wechat_html,
        cover_media_id=cover_media_id,
        digest="" if args.no_digest else info["digest"],
        author=args.author,
        source_url=source_url,
    )

    if draft_media_id:
        print(f"  ✓ 草稿创建成功！")
        print(f"  media_id: {draft_media_id}")

        # 发布成功后清理临时文件
        from cleanup_temp import wechat as _cleanup_wechat
        _cleanup_wechat(issue_date)

        if not args.full:
            print(f"  📝 {mode_label}模式草稿已创建，需配置：声明原创 + 合集 + 关闭广告 + 原文链接")
            print(f"  💡 用 Playwright 脚本自动配置：")
            print(f"     python3 resources/wechat_draft_config.py {draft_media_id} --source-url {source_url}")

        if args.publish:
            print("\n  发布草稿...")
            publish_draft(token, draft_media_id)

    print("\n" + "=" * 60)
    print("✅ 完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
