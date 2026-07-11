#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""往期周刊全文版发布到微信公众号。

"50期后自动免费"规则：每期新周刊发布时先发简化版到微信公众号（仅标题摘要），
50期后再将全文版（含完整描述、图片、往年回顾等）重新发布到公众号。

此脚本编排全流程：确定目标期数 → 找到全文版 → 预处理 → 微信 API 创建草稿。

用法:
  python3 resources/republish_full_weekly.py                # 自动计算 N-50
  python3 resources/republish_full_weekly.py --issue 103    # 指定期数
  python3 resources/republish_full_weekly.py --dry-run      # 仅预览，不创建草稿
  python3 resources/republish_full_weekly.py --publish      # 创建草稿并立即发布
  python3 resources/republish_full_weekly.py --force        # 即使已发布过也重新发布
"""

import re
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

# 将项目根目录和 resources 目录加入路径，以便导入 wechat_publish
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "resources"))


# ===== 微信发布固定模板 =====

# 头部模板：引导关注文字 + 小报童小程序卡片
# 第一行独立居中、小字号，Python猫 和 1 突出显示
# 其余行中 "9" 和 "1" 突出显示
WECHAT_HEADER_HTML = (
    '<p style="text-align:center;margin:0 0 8px;padding:0;color:#8b8378;font-family:\'PingFang SC\',-apple-system,BlinkMacSystemFont,\'Helvetica Neue\',sans-serif;font-size:13px;line-height:1.5;letter-spacing:0.04em;">△△微信关注"<strong style="color:#306998;font-weight:700;">Python猫</strong>"，回复"<strong style="color:#d4a017;font-weight:700;">1</strong>"领取电子书</p>'
    '<section style="margin:0 0 20px;padding:12px 16px 12px 20px;border-left:3px solid #306998;background:rgba(48,105,152,0.04);">'
    '<p style="color:#777777;font-family:\'PingFang SC\',-apple-system,BlinkMacSystemFont,\'Helvetica Neue\',sans-serif;font-size:15px;line-height:1.85;letter-spacing:0.04em;margin:4px 0;padding:0;">这里分享的是 Python 潮流周刊免费开源的往期全文，原文发布于一年前。我们的付费专栏内容在发布一年后会免费开源，不少内容依然值得回看，愿大家读有所获。点击文末"阅读原文"，在网页里查看，体验更佳。</p>'
    '<p style="color:#777777;font-family:\'PingFang SC\',-apple-system,BlinkMacSystemFont,\'Helvetica Neue\',sans-serif;font-size:15px;line-height:1.85;letter-spacing:0.04em;margin:4px 0;padding:0;">温馨提示：在微信关注 Python猫，发送一个数字"<strong style="color:#d4a017;font-weight:700;">9</strong>"，即可领取 9 折优惠券，订阅专栏可享 15 元优惠。订阅后可查看全部已公开和未公开内容！</p>'
    '<p style="color:#777777;font-family:\'PingFang SC\',-apple-system,BlinkMacSystemFont,\'Helvetica Neue\',sans-serif;font-size:15px;line-height:1.85;letter-spacing:0.04em;margin:4px 0;padding:0;">关注 Python猫后，发一个数字"<strong style="color:#d4a017;font-weight:700;">1</strong>"，可免费领取已开源的往季周刊精华合集。</p>'
    '</section>'
    '<mp-common-miniprogram class="weapp_display_element js_weapp_display_element js_wx_tap_highlight" data-pluginname="insertminiprogram" data-miniprogram-path="pages/webpage/webpage?url=https%3A%2F%2Fxiaobot.net%2Fp%2Fpython_weekly%3Frefer%3D2fc438e2-33fe-44bd-aa2f-ae7d8e782dea%26name%3DPython%25E6%25BD%25AE%25E6%25B5%2581%25E5%2591%25A8%25E5%2588%258A%2520%257C%2520%25E6%25AF%258F%25E5%2591%25A8%25E8%25BF%259E%25E8%25BD%25BD%25E4%25B8%25AD" data-miniprogram-nickname="小报童投递" data-miniprogram-avatar="http://mmbiz.qpic.cn/sz_mmbiz_png/THws1QqamVHlzF6S0wcibjQZcDVyvu6PcFbSDMBfoAn4nFpJITwsFOtTvqsGLXsGiajKwGgM53S8Sh14iay9eGwKw/640?wx_fmt=png&amp;wxfrom=200" data-miniprogram-title="进入Python潮流周刊专栏" data-miniprogram-imageurl="http://mmbiz.qpic.cn/sz_mmbiz_jpg/LLRiaS9YfFTN3pZepX7zEhbKE5rpZNj3ov73icpspldANibaEMKDJhzKkhfTtPLpK93cYpPf8MfNAsIibUKgNGVy3A/0?wx_fmt=jpeg" data-miniprogram-type="card" data-miniprogram-servicetype="0" data-miniprogram-appid="wx783e6b31ada3e12b" data-miniprogram-applink="#小程序://小报童/2RNWfkYOiJnImPB" data-miniprogram-imageurlback="https%3A%2F%2Fmmbiz.qpic.cn%2Fsz_mmbiz_png%2FLLRiaS9YfFTN3pZepX7zEhbKE5rpZNj3oTS48tB9ESDUhEj42efgmlWWJA247DKLzlFL0kPoAyIg6uyiawvb5xnA%2F0%3Fwx_fmt%3Dpng" data-miniprogram-cropperinfo="%7B%22c%22%3A%7B%22x%22%3A0%2C%22y%22%3A79%2C%22x2%22%3A117%2C%22y2%22%3A172.6%2C%22w%22%3A117%2C%22h%22%3A93.6%7D%7D"></mp-common-miniprogram>'
)

# 分割图标：两个小图标，位于参考资料之后、推广内容之前
WECHAT_DIVIDER_HTML = (
    '<p style="text-align:center;margin:2em 0 1em;">'
    '<img src="https://mmbiz.qpic.cn/mmbiz/cZV2hRpuAPiaJQXWGyC9wrUzIicibgXayrgibTYarT3A1yzttbtaO0JlV21wMqroGYT3QtPq2C7HMYsvicSB2p7dTBg/640?wx_fmt=gif&amp;tp=webp&amp;wxfrom=5&amp;wx_lazy=1#imgIndex=3" style="width:auto;height:auto;max-width:100%;display:inline-block;vertical-align:middle;margin:0 4px;" alt="divider">'
    '<img src="https://mmbiz.qpic.cn/mmbiz/cZV2hRpuAPiaJQXWGyC9wrUzIicibgXayrgibTYarT3A1yzttbtaO0JlV21wMqroGYT3QtPq2C7HMYsvicSB2p7dTBg/640?wx_fmt=gif&amp;tp=webp&amp;wxfrom=5&amp;wx_lazy=1#imgIndex=3" style="width:auto;height:auto;max-width:100%;display:inline-block;vertical-align:middle;margin:0 4px;" alt="divider">'
    '</p>'
)

# 尾部模板：推荐文字 + 推广图片（在参考资料、分割图标之后）
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


# ===== 链接→脚注转换（HTML 后处理） =====

# 脚注上标样式（匹配 python-weekly inkpress 主题）
SUP_STYLE = "font-size:0.75em;line-height:0;vertical-align:super;color:#306998;"

# 参考资料 section 样式（无 border-top，H2 标题的 border-bottom 已做视觉分隔）
REF_SECTION_STYLE = "margin-top:1em;padding-top:1em;"

# 参考资料列表样式（用 <p> 标签，避免 WeChat <ol> 渲染异常）
REF_LIST_STYLE = "margin:0;padding-left:0;"

# 参考资料项样式
REF_ITEM_STYLE = "font-size:0.85em;color:#8b8378;line-height:1.6;margin-bottom:0.3em;padding:0;text-align:left;"

# 参考资料标题样式
REF_TITLE_STYLE = "margin:1em 0 0.6em;padding:0.4em 0 0.4em 14px;border-left:4px solid #306998;border-bottom:1px solid rgba(212,160,23,0.3);font-size:18px;font-weight:700;line-height:1.4;color:#1a365d;letter-spacing:0.03em;"

# 参考链接内链样式
REF_LINK_STYLE = "color:#306998;text-decoration:none;margin-left:0.3em;"


def _extract_body(html: str) -> tuple[str, str, str]:
    """从完整 HTML 中提取 body 内容。

    Returns:
        (prefix, body_content, suffix)
    """
    body_match = re.search(r'(<body[^>]*>)(.*?)(</body>)', html, re.DOTALL)
    if body_match:
        body_open = html[:body_match.start(2)]
        body_content = body_match.group(2)
        body_close = html[body_match.end(2):]
        return body_open, body_content, body_close
    return "", html, ""


def convert_links_to_footnotes(html: str) -> str:
    """将 HTML 中的 <a href> 链接转换为上标脚注格式。

    WeChat 公众号不支持外部链接，所有链接需转为脚注引用。

    处理规则：
    - <a href="url">text</a> → text<sup>[N]</sup>
    - 相同 URL 使用相同脚注编号
    - 脚注定义收集到文末"参考资料"章节
    - H2/H3 内的链接也正常转换（保留标题文字）

    Args:
        html: inkpress 生成的完整 HTML 页面

    Returns:
        链接已替换为脚注的 HTML
    """
    prefix, body, suffix = _extract_body(html)

    # Step 1: 收集所有链接，建立 URL→(number, label) 映射
    link_pattern = re.compile(
        r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"[^>]*>(.*?)</a>',
        re.DOTALL,
    )

    url_to_num: OrderedDict[str, tuple[int, str]] = OrderedDict()
    # 收集所有匹配，保留顺序
    matches = list(link_pattern.finditer(body))

    for match in matches:
        url = match.group(1)
        label = match.group(2).strip()
        # 清理 label 中的 HTML 标签（如 <code> 等）
        label = re.sub(r'<[^>]+>', '', label)
        if url not in url_to_num:
            url_to_num[url] = (len(url_to_num) + 1, label)

    if not url_to_num:
        # 没有链接，无需转换
        return html

    # Step 2: 替换 body 中的链接为脚注引用
    def replace_link(match, url_map=url_to_num):
        url = match.group(1)
        label = match.group(2).strip()
        if url in url_map:
            num = url_map[url][0]
            return f'{label}<sup style="{SUP_STYLE}">[{num}]</sup>'
        return match.group(0)  # 不应该到这里

    body = link_pattern.sub(replace_link, body)

    # Step 3: 构建"参考资料"章节
    # 使用 <p> 标签替代 <ol><li>，避免 WeChat 列表渲染异常（如奇偶项丢失）。
    # 不使用 <a> 标签（微信会剥离外部链接），URL 直接作为纯文本。
    ref_items = []
    for url, (num, label) in url_to_num.items():
        ref_items.append(
            f'<p style="{REF_ITEM_STYLE}">'
            f'[{num}] {label}: {url}'
            f'</p>'
        )

    ref_section = (
        f'<h2 style="{REF_TITLE_STYLE}">参考资料</h2>\n'
        f'<section style="{REF_SECTION_STYLE}">\n'
        + '\n'.join(ref_items) +
        f'\n</section>'
    )

    # Step 4: 将参考资料章节插入到 body 末尾（在 </section> 结束标签之前）
    # inkpress 的 body 结构: <section style="container..."> ... </section>
    # 将参考资料插入到 container section 结束前
    container_close = '</section>'
    last_section_idx = body.rfind(container_close)
    if last_section_idx != -1:
        body = body[:last_section_idx] + '\n' + ref_section + body[last_section_idx:]
    else:
        body += '\n' + ref_section

    return prefix + body + suffix


# ===== 期数定位 =====

def scan_weekly_issues() -> list[tuple[str, Path, int]]:
    """扫描 docs/ 目录下所有周刊文件，按日期排序。

    Returns:
        [(date_str, filepath, issue_number), ...] 按日期升序排列
    """
    docs_dir = PROJECT_ROOT / "docs"
    weekly_files = sorted(docs_dir.glob("????-??-??-weekly.md"))

    issues = []
    for i, fp in enumerate(weekly_files, 1):
        m = re.match(r"(\d{4}-\d{2}-\d{2})-weekly\.md$", fp.name)
        if m:
            issues.append((m.group(1), fp, i))
    return issues


def find_target_issue(
    issues: list[tuple[str, Path, int]],
    issue_no: int | None = None,
) -> tuple[str, Path, int] | None:
    """确定要发布的目标期数。

    Args:
        issues: scan_weekly_issues() 的返回结果
        issue_no: 手动指定的期数，None 则自动计算 N-50

    Returns:
        (date_str, filepath, issue_number) 或 None
    """
    if not issues:
        return None

    latest_date, latest_fp, latest_no = issues[-1]

    if issue_no is not None:
        for date_str, fp, no in issues:
            if no == issue_no:
                return (date_str, fp, no)
        print(f"❌ 未找到第 {issue_no} 期")
        return None

    target_no = latest_no - 50
    if target_no < 1:
        print(f"❌ 目标期数 {target_no} 无效（最新 {latest_no} 期，少于 50 期）")
        return None

    for date_str, fp, no in issues:
        if no == target_no:
            return (date_str, fp, no)

    print(f"❌ 未找到第 {target_no} 期对应的文件")
    return None


def find_full_version(date_str: str) -> tuple[Path | None, bool]:
    """查找指定日期的全文版 Markdown 文件。

    优先查找 docs/tmp/（含 Astro frontmatter 的付费版），
    降级查找 docs/（公开版，可能已是全文或简化版）。

    Returns:
        (filepath, from_tmp) — from_tmp=True 表示含 Astro frontmatter
    """
    tmp_file = PROJECT_ROOT / "docs" / "tmp" / f"{date_str}-weekly.md"
    docs_file = PROJECT_ROOT / "docs" / f"{date_str}-weekly.md"

    if tmp_file.exists():
        return tmp_file, True
    elif docs_file.exists():
        return docs_file, False
    return None, False


# ===== 内容预处理 =====

def _extract_title_from_fm(fm_lines: list[str]) -> str | None:
    """从 frontmatter 行中提取 title 字段的值。"""
    for line in fm_lines:
        m = re.match(r"title:\s*['\"]?(.+?)['\"]?\s*$", line)
        if m:
            return m.group(1)
    return None


def _body_starts_with_h1(body_lines: list[str]) -> bool:
    """检查正文是否以 H1 标题开头。"""
    for bl in body_lines:
        stripped = bl.strip()
        if stripped == "":
            continue
        return stripped.startswith("# ")
    return False


def strip_frontmatter(content: str, from_tmp: bool = False) -> tuple[str, str | None]:
    """去除 Markdown 文件的 YAML frontmatter。

    对于 tmp 文件（Astro frontmatter）：去除 layout/tags/theme/featured

    对于 docs 文件（简单 frontmatter）：移除整个 frontmatter 块

    Returns:
        (清洗后的内容, 从 frontmatter 中提取的 title，可能为 None)
    """
    if not content.strip().startswith("---"):
        return content, None

    lines = content.split("\n")

    # 定位第二个 ---（frontmatter 结束标记）
    end_idx = None
    fm_started = False
    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not fm_started:
                fm_started = True
            else:
                end_idx = i
                break

    if end_idx is None:
        return content, None  # 格式异常，原样返回

    fm_lines = lines[1:end_idx]  # frontmatter 内部行
    body_lines = lines[end_idx + 1:]  # 正文

    title_from_fm = _extract_title_from_fm(fm_lines)

    # 清理正文开头的空行
    while body_lines and body_lines[0].strip() == "":
        body_lines.pop(0)

    # 注意：不再自动添加 H1 标题，微信正文不需要标题
    # 标题从 frontmatter 提取后用于微信 API 的 title 字段

    # 不保留任何 frontmatter 字段到 WeChat 正文中。
    # title 已通过 fm_title 返回用于 API title 字段，
    # description/author/pubDate 分别由 API digest/author 字段或 extract_article_info 处理。
    # 若保留 mini frontmatter，inkpress 会将其渲染为可见文本，污染正文。

    return "\n".join(body_lines), title_from_fm


def is_full_version(content: str) -> bool:
    """启发式判断内容是否已是全文版（含文章描述）。

    简化版的标志是"以下是本期标题摘要"或仅有序号标题无描述文字。
    全文版有"你好，我是猫哥"或每篇文章后有描述段落。
    """
    # 简化版的明显标志
    if "以下是本期摘要" in content or "以下是本期标题摘要" in content:
        return False
    # 全文版标志：个性化问候
    if "你好，我是猫哥" in content:
        return True
    # 如果内容足够长（>3000 字符），大概率是全文版
    if len(content) > 3000:
        return True
    return False


# ===== 文章标题加粗预处理 =====

def bold_article_titles(content: str) -> str:
    """将文章/项目标题行加粗，使其区别于描述文字。

    匹配模式：
      N、[Title](url)      → **N、[Title](url)**
      N. [Title](url)      → **N. [Title](url)**

    处理后的行会被 inkpress 渲染为 <strong> 包裹，在微信中显示为粗体。
    链接仍保留，后续由 convert_links_to_footnotes 转为脚注引用。
    """
    import re as _re

    # 匹配: 行首 + 数字 + 分隔符（、或.） + Markdown 链接
    # 例如: 1、[Python 工具链管理](url) 或 1. [项目名](url)
    pattern = _re.compile(
        r'^(\d+[、．.])'           # 序号 + 分隔符
        r'\s*'                      # 可选空格
        r'(\[.+?\]\(.+?\))'         # Markdown 链接 [text](url)
        r'$',                       # 行尾
        _re.MULTILINE,
    )

    def _bold_match(m: _re.Match) -> str:
        return f'**{m.group(1)}{m.group(2)}**'

    return pattern.sub(_bold_match, content)


# ===== 发布追踪 =====

def load_republish_tracking() -> dict:
    """加载发布追踪文件，记录哪些期已发布过全文版。"""
    tracking_file = PROJECT_ROOT / "docs" / "tmp" / "republished.json"
    if tracking_file.exists():
        try:
            return json.loads(tracking_file.read_text())
        except (json.JSONDecodeError, KeyError):
            pass
    return {"republished": {}}


def save_republish_tracking(tracking: dict) -> None:
    """保存发布追踪文件。"""
    tracking_file = PROJECT_ROOT / "docs" / "tmp" / "republished.json"
    tracking_file.parent.mkdir(parents=True, exist_ok=True)
    tracking_file.write_text(json.dumps(tracking, ensure_ascii=False, indent=2))


def is_already_published(date_str: str, tracking: dict) -> bool:
    """检查指定日期是否已发布过全文版。"""
    return date_str in tracking.get("republished", {})


# ===== 草稿自动配置 =====

def _auto_config_draft(draft_media_id: str, source_url: str, issue_no: int) -> bool:
    """通过 Playwright CDP 自动配置草稿：原创声明、合集、原文链接。

    需要 Edge 浏览器已开启 CDP 调试端口 (localhost:18800)。
    如果浏览器未运行或配置失败，返回 False 并打印手动操作指引。
    """
    import subprocess

    config_script = PROJECT_ROOT / "resources" / "wechat_draft_config.py"
    if not config_script.exists():
        print(f"  ⚠️ 配置脚本不存在: {config_script}")
        return False

    # 尝试自动配置
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(config_script),
                draft_media_id,
                "--full",
                "--source-url", source_url,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(result.stderr or result.stdout)
            return False
    except subprocess.TimeoutExpired:
        print("  ⚠️ 自动配置超时（60s）")
        return False
    except Exception as e:
        print(f"  ⚠️ 自动配置异常: {e}")
        return False


# ===== 主流程 =====

def main():
    parser = argparse.ArgumentParser(
        description="往期周刊全文版发布到微信公众号",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 resources/republish_full_weekly.py                # 自动计算 N-50
  python3 resources/republish_full_weekly.py --issue 103    # 指定期数
  python3 resources/republish_full_weekly.py --dry-run      # 仅预览
  python3 resources/republish_full_weekly.py --publish      # 创建草稿并发布
        """,
    )
    parser.add_argument(
        "--issue", type=int,
        help="指定期数（默认自动计算：最新期数 - 50）",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="仅预览预处理后的内容，不创建微信草稿",
    )
    parser.add_argument(
        "--publish", action="store_true",
        help="创建草稿后立即发布（默认仅创建草稿）",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="即使已发布过也重新发布",
    )
    parser.add_argument(
        "--skip-image-upload", action="store_true",
        help="跳过图片上传（使用原始 URL）",
    )
    parser.add_argument(
        "--theme", default="python-weekly-v2",
        help="inkpress 主题名称（默认: python-weekly-v2）",
    )

    args = parser.parse_args()

    # ---- Step 1: 确定目标期数 ----
    issues = scan_weekly_issues()
    if not issues:
        print("❌ 未找到任何周刊文件（docs/*-weekly.md）")
        sys.exit(1)

    target = find_target_issue(issues, args.issue)
    if not target:
        sys.exit(1)

    date_str, docs_fp, issue_no = target
    latest_no = issues[-1][2]
    print(f"📋 最新期数: 第 {latest_no} 期")
    print(f"🎯 目标期数: 第 {issue_no} 期 ({date_str})")

    # ---- Step 2: 检查是否已发布 ----
    tracking = load_republish_tracking()
    if is_already_published(date_str, tracking) and not args.force:
        info = tracking["republished"][date_str]
        print(f"\n⚠️  第 {issue_no} 期已于 {info.get('date', '未知日期')} 发布过全文版")
        print(f"   WeChat media_id: {info.get('wechat_media_id', '未知')}")
        print(f"   如需重新发布，请使用 --force")
        sys.exit(0)

    # ---- Step 3: 查找全文版 ----
    full_fp, from_tmp = find_full_version(date_str)
    if not full_fp:
        print(f"\n❌ 未找到第 {issue_no} 期的全文版文件")
        print(f"   尝试过: docs/tmp/{date_str}-weekly.md")
        print(f"   尝试过: docs/{date_str}-weekly.md")
        sys.exit(1)

    source_label = "docs/tmp/ (Astro frontmatter)" if from_tmp else "docs/ (标准格式)"
    print(f"📄 全文版来源: {source_label}")

    # ---- Step 4: 预处理 ----
    raw_content = full_fp.read_text(encoding="utf-8")
    clean_content, fm_title = strip_frontmatter(raw_content, from_tmp)

    # 移除正文中的 H1 标题行（标题通过微信 API title 字段设置）
    lines = clean_content.split("\n")
    if lines and lines[0].strip().startswith("# "):
        # 如果 frontmatter 没提取到 title，从 H1 行提取
        if not fm_title:
            fm_title = lines[0].strip().replace("# ", "").strip()
        lines.pop(0)  # 移除 H1 行
        # 清理后续空行
        while lines and lines[0].strip() == "":
            lines.pop(0)
        clean_content = "\n".join(lines)

    # 将文章/项目标题行加粗，使其区别于描述文字
    clean_content = bold_article_titles(clean_content)

    # 拼接微信发布固定模板：仅拼接正文（头部/尾部在 HTML 后处理阶段插入）
    # 不再在此处拼接头部 HTML，避免 inkpress 处理 WeChat 专用元素

    if not from_tmp and not is_full_version(clean_content):
        print(f"\n⚠️  警告: 文件似乎是简化版（仅有标题摘要），非全文版")
        print(f"   如果确实要发布此版本，请继续。否则 Ctrl+C 取消。")
        if not args.dry_run:
            try:
                input("按 Enter 继续，Ctrl+C 取消...")
            except KeyboardInterrupt:
                print("\n已取消")
                sys.exit(0)

    # 写入预处理后的文件
    output_fp = PROJECT_ROOT / "docs" / "tmp" / f"{date_str}-weekly-wechat.md"
    output_fp.parent.mkdir(parents=True, exist_ok=True)
    output_fp.write_text(clean_content, encoding="utf-8")
    print(f"🔧 预处理后: {output_fp.relative_to(PROJECT_ROOT)}")
    print(f"   内容长度: {len(clean_content)} 字符")

    if args.dry_run:
        preview_len = min(600, len(clean_content))
        print(f"\n🔍 Dry-run — 内容预览（前 {preview_len} 字符）:")
        print("-" * 50)
        print(clean_content[:preview_len])
        if len(clean_content) > preview_len:
            print(f"... (共 {len(clean_content)} 字符)")
        print("-" * 50)
        print(f"\n✅ Dry-run 完成。预处理文件已保存到: {output_fp.relative_to(PROJECT_ROOT)}")
        return

    # ---- Step 5: 通过微信 API 创建草稿 ----
    from wechat_publish import (
        get_access_token,
        extract_article_info,
        extract_image_urls,
        upload_image_to_wechat,
        convert_md_to_wechat_html,
        replace_images_in_html,
        create_draft,
        publish_draft,
    )

    print("\n" + "=" * 60)
    print("📡 通过微信 API 创建草稿")
    print("=" * 60)

    # 5a. 获取 token
    print("\n[1/5] 获取 access_token...")
    token = get_access_token()
    print(f"  ✓ token: {token[:16]}...")

    # 5b. 提取文章元信息
    print("\n[2/5] 提取文章信息...")
    info = extract_article_info(clean_content, output_fp)
    # 优先使用 frontmatter/H1 提取的标题（比 extract_article_info 的文件名回退更准确）
    if fm_title:
        info["title"] = fm_title
    # 往期回顾标题格式
    info["title"] = f"【往期回顾】{info['title']}"
    print(f"  标题: {info['title']}")
    if info["digest"]:
        print(f"  摘要: {info['digest'][:80]}...")
    if info["cover_url"]:
        print(f"  封面图: {info['cover_url'][:80]}")

    # 5c. 上传图片到微信素材库
    image_map: dict[str, str] = {}
    cover_media_id = ""

    if not args.skip_image_upload:
        print("\n[3/5] 上传图片到微信素材库...")
        image_urls = extract_image_urls(clean_content)
        if image_urls:
            print(f"  共 {len(image_urls)} 张图片")
            for i, img_url in enumerate(image_urls, 1):
                print(f"  [{i}/{len(image_urls)}] ", end="")
                media_id, wechat_url = upload_image_to_wechat(img_url, token)
                if media_id:
                    image_map[img_url] = wechat_url
                    if i == 1 and img_url == info["cover_url"]:
                        cover_media_id = media_id
                time.sleep(0.3)
        else:
            print("  无图片需要上传")
    else:
        print("\n[3/5] 跳过图片上传 (--skip-image-upload)")

    # 5d. Markdown → 微信 HTML（inkpress 主题引擎）
    print(f"\n[4/5] Markdown → 微信 HTML（主题: {args.theme}）→ 链接转脚注 → 拼接头尾...")
    wechat_html = convert_md_to_wechat_html(clean_content, theme=args.theme)

    # 替换图片 URL
    if image_map:
        wechat_html = replace_images_in_html(wechat_html, image_map)
        replaced = sum(1 for v in image_map.values() if v)
        print(f"  ✓ 替换了 {replaced} 张图片为微信 CDN URL")

    # 提取 inkpress 生成的 container section 内容
    # inkpress 输出结构: <body><section style="container..."> ... </section></body>
    container_match = re.search(
        r'(<body[^>]*>\s*<section[^>]*>)(.*?)(</section>\s*</body>)',
        wechat_html, re.DOTALL
    )
    if container_match:
        body_prefix = wechat_html[:container_match.start(2)]
        body_content = container_match.group(2)
        body_suffix = wechat_html[container_match.end(2):]
        # 缩减顶部空白：body padding → 0，容器顶部内边距 → 0
        # 同时去除 <body> 与 <section> 之间的换行和缩进（WeChat 编辑器会渲染为空白）
        body_prefix = body_prefix.replace(
            'padding: 12px;',
            'padding: 0;',
        ).replace(
            'padding: 20px 16px',
            'padding: 0 16px 20px 16px',
        ).replace(
            '>\n  <section',
            '><section',
        )
    else:
        body_prefix = wechat_html[:0] if False else ""
        body_content = wechat_html
        body_suffix = ""

    # 先转换链接为脚注（仅正文内容，避免影响头部/尾部模板中的微信内部链接）
    # 重建临时完整 HTML 用于脚注转换
    if container_match:
        temp_html = body_prefix + body_content + body_suffix
        wechat_html = convert_links_to_footnotes(temp_html)
        # 重新提取 body_content
        container_match2 = re.search(
            r'(<body[^>]*>\s*<section[^>]*>)(.*?)(</section>\s*</body>)',
            wechat_html, re.DOTALL
        )
        if container_match2:
            body_prefix = wechat_html[:container_match2.start(2)]
            body_content = container_match2.group(2)
            body_suffix = wechat_html[container_match2.end(2):]
    else:
        wechat_html = convert_links_to_footnotes(wechat_html)
        body_content = wechat_html
    print(f"  ✓ 链接已转换为脚注引用")

    # 在 body_content 开头插入头部模板（引导关注 + 小程序卡片）
    body_content = WECHAT_HEADER_HTML + body_content

    # 重新组装完整 HTML（尾部模板放在容器内部，微信编辑器保留 linktype="image"）
    body_content += WECHAT_DIVIDER_HTML + WECHAT_FOOTER_HTML
    wechat_html = body_prefix + body_content + body_suffix

    # 保存 HTML 副本
    html_fp = output_fp.with_suffix(".wechat.html")
    html_fp.write_text(wechat_html, encoding="utf-8")
    print(f"  HTML 已保存到: {html_fp.relative_to(PROJECT_ROOT)}")
    print(f"  HTML 长度: {len(wechat_html)} 字符")

    # 5e. 创建草稿（携带原文链接）
    source_url = f"https://pythoncat.top/posts/{date_str}-weekly"
    print(f"  原文链接: {source_url}")

    draft_media_id = create_draft(
        token=token,
        title=info["title"],
        content_html=wechat_html,
        cover_media_id=cover_media_id,
        digest=info["digest"],
        author="豌豆花下猫",
        source_url=source_url,
    )

    if not draft_media_id:
        print("\n❌ 草稿创建失败")
        sys.exit(1)

    print(f"\n✅ 草稿创建成功！")
    print(f"   media_id: {draft_media_id}")

    # 自动配置：原创声明、合集、广告、原文链接（通过 Playwright CDP）
    print(f"\n🔧 配置草稿（原创+合集+原文链接）...")
    config_ok = _auto_config_draft(draft_media_id, source_url, issue_no)
    if config_ok:
        print(f"  ✓ 草稿配置完成")
    else:
        print(f"  ⚠️ 自动配置失败，请手动配置或运行：")
        print(f"     python3 resources/wechat_draft_config.py {draft_media_id} --full --source-url {source_url}")

    # 记录追踪
    tracking["republished"][date_str] = {
        "issue": issue_no,
        "wechat_media_id": draft_media_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
    }
    tracking["last_republished_issue"] = issue_no
    save_republish_tracking(tracking)

    # 5f. 可选发布
    if args.publish:
        print("\n📢 立即发布草稿...")
        success = publish_draft(token, draft_media_id)
        if success:
            print("  ✓ 发布成功！")
        else:
            print("  ⚠️ 发布失败，请手动在后台操作")

    print("\n" + "=" * 60)
    print("✅ 全部完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
