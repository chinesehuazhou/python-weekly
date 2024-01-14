import httpx
import asyncio
import feedparser
import os
from datetime import datetime, timedelta
from dotenv.main import load_dotenv
from telegram import Bot

if not os.getenv('TG_BOT_TOKEN') or not os.getenv('TG_CHAT_ID'):
    load_dotenv()

feeds = {
    "Python 潮流周刊": "https://pythoncat.top/rss.xml",
    "Python Weekly": "https://us2.campaign-archive.com/feed?u=e2e180baf855ac797ef407fc7&id=9e26887fc5",
    "Awesome Python Weekly": "https://python.libhunt.com/newsletter/feed",
    "Python Hub Weekly Digest": "https://pythonhub.dev/digest/feed/",
    "Python recap for week": "https://kill-the-newsletter.com/feeds/i6vmi2anfvwbi05d.xml",
    "Pycoders Weekly": "https://pycoders.com/feed",
    "Django News": "https://django-news.com/issues.rss",
    "Data Science Weekly": "https://datascienceweekly.substack.com/feed"
}


async def get_last_issue_async(client, name, url):
    """异步获取周刊本周发布的标题和链接"""
    try:
        response = await client.get(url, timeout=30.0)
        feed = feedparser.parse(response.text)
    except Exception as e:
        print(f"Error occurred while processing feed {url}: {type(e).__name__}, {e}")
        return name, None, None

    for entry in feed.entries:
        print(f"Handling entry from {name}...")
        title, link = process_entry(entry)
        if title and link:
            return name, title, link

    print(f"{url} 取不到本周发布的周刊！")
    print(feed)
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


async def set_weekly_news():
    """异步组装每期周刊要发布的内容"""
    header = set_header()
    footer = set_footer()
    news_items = []

    async with httpx.AsyncClient() as client:
        tasks = [get_last_issue_async(client, name, url) for name, url in feeds.items()]
        results = await asyncio.gather(*tasks)

    for name, title, link in results:
        if title and link:
            if not title.startswith(name):
                title = name + " " + title
            news_items.append((title, link))

    news_items = [f"{chr(9311 + i)} [{title}]({link})" for i, (title, link) in enumerate(news_items, start=1)]

    weekly_news = '\n\n'.join(news_items)
    return f"{header}\n\n{weekly_news}\n\n{footer}"


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


async def send_to_telegram(text):
    tg_bot_token = os.environ['TG_BOT_TOKEN']
    tg_chat_id = os.environ['TG_CHAT_ID']
    bot = Bot(tg_bot_token)
    print("Sending content to tg bot")
    await bot.send_message(chat_id=tg_chat_id, text=text, parse_mode='Markdown', disable_web_page_preview=True)


def main():
    news = asyncio.run(set_weekly_news())
    print(news)
    asyncio.run(send_to_telegram(news))


main()
