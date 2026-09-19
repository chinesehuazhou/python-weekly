"""周刊汇聚：把最近一周发布的各 Python 周刊链接汇总，发送到 Telegram 频道。

**执行时机**：`python-weekly-release` 阶段五——astro-blog 推送成功、新一期上线之后。
不再由 GitHub Actions 定时任务驱动（原 `.github/workflows/weekly_collection_job.yml` 已废弃删除）。

**本刊条目的来源**：不再依赖 `pythoncat.top/rss.xml`。该 RSS 挂在 Vercel CDN 上
（`cache-control: public, max-age=14400`），发布后最长 4 小时内边缘缓存仍是旧副本，
读到的还是上一期；而上一期往往已超出 7 天窗口被过滤掉，导致本刊条目整个消失。
现在改为本地取：标题读 astro-blog/docs 的当期文件，链接按日期拼（或由 --own-url 显式给）。
传 `--date` 即可；不传时才回退到 RSS（并用时间戳绕过 CDN 缓存）。

用法：
    .venv/bin/python resources/weekly_collection.py --date 2026-09-19 --issue 168
    .venv/bin/python resources/weekly_collection.py --date 2026-09-19 --dry-run
    .venv/bin/python resources/weekly_collection.py            # 兜底：走 RSS
"""

import argparse
import asyncio
import os
import re
import sys
from datetime import datetime, timedelta

import feedparser
import httpx
from dotenv.main import load_dotenv
from telegram import Bot

if not os.getenv('TG_BOT_TOKEN') or not os.getenv('TG_CHAT_ID'):
    load_dotenv()

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASTRO_POSTS = os.path.expanduser('~/Documents/GitHub/astro-blog/src/pages/posts')

feeds = {
    "Python 潮流周刊": "https://pythoncat.top/rss.xml",
    "Python Weekly": "https://kill-the-newsletter.com/feeds/h9fwp3i8gj6djygelscq.xml",
    "Awesome Python Weekly": "https://python.libhunt.com/newsletter/feed",
    "Python Hub Weekly Digest": "https://pythonhub.dev/digest/feed/",
    "Python recap for week": "https://kill-the-newsletter.com/feeds/i6vmi2anfvwbi05d.xml",
    "Pycoders Weekly": "https://pycoders.com/feed",
    "Django News": "https://django-news.com/issues.rss",
    "Data Science Weekly": "https://datascienceweekly.substack.com/feed"
}

# 除本刊外的其它订阅源
OTHER_FEEDS = {k: v for k, v in feeds.items() if k != "Python 潮流周刊"}


def read_local_title(date_str):
    """从当期落盘文件里取本刊标题（含 #期号 的完整标题）。

    读取顺序：astro-blog 博客版 → docs/ 简化版 → docs/tmp/ 全文归档。
    返回 None 表示都读不到。
    """
    candidates = [
        os.path.join(ASTRO_POSTS, f'{date_str}-weekly.md'),
        os.path.join(REPO_ROOT, 'docs', f'{date_str}-weekly.md'),
        os.path.join(REPO_ROOT, 'docs', 'tmp', f'{date_str}-weekly.md'),
    ]
    for path in candidates:
        if not os.path.isfile(path):
            continue
        with open(path, encoding='utf-8') as f:
            head = f.read(4000)
        m = re.search(r"^title:\s*['\"]?(.+?)['\"]?\s*$", head, re.M)
        if m:
            title = m.group(1).strip()
            # 全文版标题可能是「中文标题---English Title」，汇聚只取中文侧
            title = title.split('---')[0].strip()
            if title:
                return title, os.path.relpath(path, REPO_ROOT)
    return None, None


def build_own_entry(date_str, issue_no, own_url):
    """组装本刊条目 (title, link)，优先本地，其次 RSS。"""
    link = own_url or (f"https://pythoncat.top/posts/{date_str}-weekly/" if date_str else None)

    title, src = read_local_title(date_str) if date_str else (None, None)
    if title:
        print(f"[本刊] 标题取自本地 {src}: {title}")
    elif issue_no:
        title = f"Python 潮流周刊#{issue_no}"
        print(f"[本刊] 本地读不到标题，回退为期号标题: {title}")

    if title and link:
        return title, link

    print("[本刊] 本地取不到（缺 --date 或缺落盘文件），回退到 RSS")
    return None


async def get_last_issue_async(client, name, url):
    """异步获取周刊本周发布的标题和链接"""
    if "pythoncat.top" in url:
        # 仅兜底路径会走到这里：加时间戳绕过 Vercel CDN 的 4 小时边缘缓存
        url = f"{url}?t={int(datetime.now().timestamp())}"
    try:
        # 使用浏览器 UA 避免被 Cloudflare 等 CDN 拦截
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; PythonWeeklyBot/1.0; "
                "+https://github.com/chinesehuazhou/python-weekly)"
            )
        }
        response = await client.get(url, timeout=30.0, headers=headers)
        response.encoding = 'utf-8'
        feed = feedparser.parse(response.text)
    except Exception as e:
        print(f"Error occurred while processing feed {url}: {type(e).__name__}, {e}")
        return name, None, None

    # 收集所有在 7 天窗口内的条目，优先选择带有 #数字 编号的正刊
    candidates = []  # (title, link, is_weekly)
    for entry in feed.entries:
        print(f"Handling entry from {name}...")
        title, link = process_entry(entry)
        if title and link:
            # 检查标题是否像正刊（含 #数字 模式，如 "#153："）
            is_weekly = bool(re.search(r'#\d+', title))
            candidates.append((title, link, is_weekly))

    if candidates:
        # 优先返回正刊，否则返回第一个候选
        candidates.sort(key=lambda x: x[2], reverse=True)
        title, link, is_weekly = candidates[0]
        if not is_weekly:
            print(f"[{name}] 未找到正刊条目，使用最近条目: {title}")
        return name, title, link

    print(f"{url} 取不到本周发布的周刊！")
    return name, None, None


def process_entry(entry):
    published_parsed = getattr(entry, 'published_parsed', None)
    updated_parsed = getattr(entry, 'updated_parsed', None)
    # pubDate
    parsed_time = published_parsed if published_parsed else updated_parsed
    if parsed_time:
        published = datetime(*parsed_time[:6])
        if datetime.now() - published <= timedelta(days=7):
            print(entry.title)
            return entry.title, entry.link
    return None, None


async def set_weekly_news(own=None):
    """异步组装每期周刊要发布的内容。own 为 (title, link) 时作为第 ① 条。"""
    header = set_header()
    footer = set_footer()
    news_items = []

    if own:
        news_items.append(own)

    async with httpx.AsyncClient() as client:
        tasks = [get_last_issue_async(client, name, url) for name, url in OTHER_FEEDS.items()]
        results = await asyncio.gather(*tasks)

    for name, title, link in results:
        if title and link:
            if not title.startswith(name):
                title = name + " " + title
            news_items.append((title, link))

    news_items = [f"{chr(9311 + i)} [{title}]({link})" for i, (title, link) in enumerate(news_items, start=1)]

    weekly_news = '\n\n'.join(news_items)
    return f"{header}\n\n{weekly_news}\n\n{footer}", len(news_items)


def get_date_range():
    today = datetime.now()
    seven_days_ago = today - timedelta(days=6)
    result = f"{seven_days_ago.strftime('%Y.%m.%d')} - {today.strftime('%Y.%m.%d')}"
    return result


def set_header():
    return "Python 社区中有不少优秀的技术周刊，这里把最近一周内发布的周刊汇集起来，供诸位 Pythonista 们丰富阅读。\n\n" \
           f"时间：{get_date_range()}"


def set_footer():
    return "🐱频道 @pythontrendingweekly"


def verify_destination():
    """发送前确认目标会话确实是频道。

    2026-09-19 教训：`.env` 里的 `TG_CHAT_ID` 是一个**私聊 id**，而 bot 又不在频道里，
    于是每次发送都"成功"地进了私聊——无异常、退出码 0、Actions 全绿，频道却永远收不到。
    这类静默错发只能靠发送前核对目标来拦住，所以在这里直接检查：
    目标必须是 channel 类型，且能查到名字，否则中止。
    """
    token = os.environ['TG_BOT_TOKEN'].strip()
    chat_id = os.environ['TG_CHAT_ID'].strip()
    try:
        r = httpx.get(f"https://api.telegram.org/bot{token}/getChat",
                      params={'chat_id': chat_id}, timeout=30).json()
    except Exception as e:
        print(f"⚠️ 目标校验请求失败（{type(e).__name__}: {e}），继续发送前请自行确认目标")
        return

    if not r.get('ok'):
        raise SystemExit(f"✗ 目标校验失败：{r.get('error_code')} {r.get('description')}\n"
                         f"  TG_CHAT_ID={chat_id} 不可达。请确认它是频道 ID（形如 -100…）")

    c = r['result']
    kind = c.get('type')
    label = c.get('title') or c.get('username') or c.get('first_name')
    if kind != 'channel':
        raise SystemExit(
            f"✗ 目标不是频道！type={kind}  name={label!r}  id={chat_id}\n"
            f"  消息会发进这个 {'私聊' if kind == 'private' else kind}，而不是频道。\n"
            f"  频道应为 @pythontrendingweekly（id -1001928222538）。已中止，未发送。")

    print(f"目标会话核对通过：{label} (@{c.get('username')}) id={chat_id}")


async def send_to_telegram(text):
    tg_bot_token = os.environ['TG_BOT_TOKEN'].strip()
    tg_chat_id = os.environ['TG_CHAT_ID'].strip()
    bot = Bot(tg_bot_token)
    print("Sending content to tg bot")
    # 显式放宽超时：默认 5s 容易假超时（请求其实已到达 TG），见 python-weekly-release skill
    await bot.send_message(chat_id=tg_chat_id, text=text, parse_mode='Markdown',
                           disable_web_page_preview=True,
                           read_timeout=60, write_timeout=60,
                           connect_timeout=60, pool_timeout=60)


def parse_args(argv):
    p = argparse.ArgumentParser(description='周刊汇聚发 Telegram 频道')
    p.add_argument('--date', help='本期日期 YYYY-MM-DD，用于定位本刊标题与博客链接')
    p.add_argument('--issue', type=int, help='本期期号，如 168（本地读不到标题时的兜底）')
    p.add_argument('--own-url', default='', help='本刊本期博客链接，不给则按日期拼 pythoncat.top')
    p.add_argument('--dry-run', action='store_true', help='只打印不发送')
    return p.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])

    own = build_own_entry(args.date, args.issue, args.own_url)
    if own is None:
        # 兜底：走 RSS 取本刊（会被 CDN 缓存影响，仅作最后手段）
        async def fetch_own():
            async with httpx.AsyncClient() as client:
                return await get_last_issue_async(client, "Python 潮流周刊", feeds["Python 潮流周刊"])
        name, title, link = asyncio.run(fetch_own())
        if title and link:
            own = (title, link)

    news, count = asyncio.run(set_weekly_news(own))
    print(news)

    # 一条周刊都没取到时不要发（通常是网络不可达），避免把空消息推送到频道。
    # ⚠️ 这里必须用条目计数判断，不要用「正文里有没有 ① 这个字符」判断：
    # 条目编号是 chr(9311 + i) 且 i 从 1 起，即从 chr(9312)（① U+2460）开始，
    # 而 chr(9311) 是 U+245F、正文里永远不出现 —— 用它判断会恒为真，
    # 脚本就会每次都打印「已中止发送」而从不真正发送（2026-09-19 踩过）。
    if count == 0:
        print("\n⚠️ 未取到任何周刊（检查网络/订阅源），已中止发送。")
        return

    print(f"\n共取到 {count} 条周刊。")
    if not own:
        print("⚠️ 第 ① 条不是本刊（本刊条目未取到），发送前请确认！")

    if args.dry_run:
        print("\n[dry-run] 已生成内容但未发送。去掉 --dry-run 才会真正发送到 Telegram。")
        return

    verify_destination()
    asyncio.run(send_to_telegram(news))


if __name__ == '__main__':
    main()
