import asyncio
import datetime
import os
import re
import sys
import yaml
import shutil
from dotenv.main import load_dotenv
from telegram import Bot, InputFile
import jieba

if not os.getenv('TG_BOT_TOKEN') or not os.getenv('TG_CHAT_ID'):
    load_dotenv()

# 固定文本常量
WEEKLY_INTRO = ("本周刊由 Python猫 出品，精心筛选国内外的 400+ 信息源，"
                "为你挑选最值得分享的文章、教程、开源项目、软件工具、播客和视频、热门话题等内容。"
                "愿景：帮助所有读者精进 Python 技术，并增长职业和副业的收入。\n\n"
                "**温馨提示：** 在微信关注 **Python猫**，发送数字“**9**”，即可领取 9 折优惠码，订阅专栏可享 15 元优惠。\n\n"
                "去专栏阅读全文：[全文链接]()")

SUBSCRIPTION_INFO = ("周刊实行付费订阅制，年费 148 元，平均每天 4 毛钱，为你精准筛选高质量技术内容。"
                    "在信息洪流中为你淘金，助力技术视野拓展和职业发展，欢迎订阅：[https://xiaobot.net/p/python_weekly](https://xiaobot.net/p/python_weekly)")

SEASON2_SUMMARY = "[Python 潮流周刊第3季总结，附电子书下载](https://pythoncat.top/posts/2025-04-20-sweekly)"

FREE_COLLECTION = "[Python 潮流周刊第二季完结（31~60）](https://pythoncat.top/posts/2025-04-20-iweekly)"

SEASON1_SUMMARY = "[Python 潮流周刊第一季精华合集（1~30）](https://pythoncat.top/posts/2023-12-11-weekly)"

WECHAT_QR = "**微信关注 Python猫**：[https://img.pythoncat.top/python_cat.jpg](https://img.pythoncat.top/python_cat.jpg)"

FOOTER_SUBSCRIPTION = ("在信息洪流中为你淘金，助力 Python 技术视野拓展和职业发展。现在订阅，每周让自己进步一点点。\n\n"
                      "👀 订阅：[小报童](https://weekly.pythoncat.top/zh/#subscribe-xiaobot)  [爱发电](https://weekly.pythoncat.top/zh/#subscribe-afdian) \n\n"
                      "👀 合集：[1季](https://pythoncat.top/posts/2023-12-11-weekly)  [2季](https://pythoncat.top/posts/2025-04-20-iweekly)  [3季](https://pythoncat.top/posts/2026-06-07-iweekly) \n\n")

# 英文版固定文本常量
WEEKLY_INTRO_EN = ("Welcome to Python Trending Weekly - your gateway to cutting-edge Python intelligence! Curated by Python Cat from 400+ premium sources worldwide, "
                   "we deliver the most valuable articles, tutorials, open-source projects, tools, podcasts, videos, and trending discussions directly to your inbox. "
                   "Our mission: Accelerate your Python mastery and unlock new career opportunities in the ever-evolving tech landscape.\n\n"
                   "**Stay ahead of the curve:** [Subscribe now](https://patreon.com/PythonCat666) for weekly insights that keep you at the forefront of Python innovation!")

SUBSCRIPTION_INFO_EN = ("Cut through the noise with our premium subscription at $4.99/month. Get hand-picked, cutting-edge Python content delivered weekly. "
                        "Join 350+ professionals who trust us to filter the best from 400+ sources for technical vision expansion and career development. "
                        "Subscribe at: [Patreon](https://patreon.com/PythonCat666)")

SEASON2_SUMMARY_EN = "[Python Trending Weekly Season 3 Summary with E-book Download](https://pythoncat.top/posts/2025-04-20-sweekly)"

FREE_COLLECTION_EN = "[Python Trending Weekly Season 2 Complete Collection (Issues 31-60)](https://pythoncat.top/posts/2025-04-20-iweekly)"

SEASON1_SUMMARY_EN = "[Python Trending Weekly Season 1 Highlights Collection (Issues 1-30)](https://pythoncat.top/posts/2023-12-11-weekly)"

FOOTER_SUBSCRIPTION_EN = ("This newsletter operates on a paid subscription model at $20 per year, with an estimated 50 issues and over 100,000 words. "
                         "Subscribe now and make progress every week.\n\n"
                         "👀 [Patreon](https://patreon.com/PythonCat666) \n\n"
                         "👀 [Free Collection Download](https://pythoncat.top/posts/2025-04-20-sweekly) \n\n")

def split_bilingual_text(text):
    """拆分 `中文---English` 形式的文本"""
    if not isinstance(text, str):
        return text, None
    if '---' not in text:
        return text.strip(), None
    chinese_text, english_text = text.split('---', 1)
    return chinese_text.strip(), english_text.strip() or None

def extract_issue_title(full_title):
    """提取周刊标题冒号后的主题部分"""
    if not full_title:
        return ''
    for sep in ('：', ':'):
        if sep in full_title:
            return full_title.split(sep, 1)[1].strip()
    return full_title.strip()

def build_english_weekly_title(full_title, weekly_no):
    """基于 `中文---English` 主标题约定构造英文周刊标题"""
    if not full_title:
        return f"Python Trending Weekly #{weekly_no}"
    title = full_title.strip()
    if title.startswith('Python Trending Weekly #'):
        return title
    issue_title = extract_issue_title(title)
    _, english_issue_title = split_bilingual_text(issue_title)
    if not english_issue_title:
        raise ValueError(
            "Front matter title must use `中文---English` format for the main weekly title, "
            f"for example: Python 潮流周刊#{weekly_no}：中文标题---English Title"
        )
    # 若英文部分已自带 "Python Trending Weekly #N" 前缀，直接返回，避免双重前缀
    prefix = f"Python Trending Weekly #{weekly_no}"
    if english_issue_title.startswith(prefix):
        return english_issue_title
    return f"{prefix}: {english_issue_title}"

def build_english_description(description):
    """将中文统计描述转换为英文描述"""
    if not description:
        return description
    article_count = int(re.search(r'(\d+)\s*篇文章', description).group(1)) if re.search(r'(\d+)\s*篇文章', description) else 0
    project_count = int(re.search(r'(\d+)\s*个开源项目', description).group(1)) if re.search(r'(\d+)\s*个开源项目', description) else 0
    audio_video_match = re.search(r'(\d+)\s*则音视频', description)
    hot_topic_match = re.search(r'(\d+)\s*[则个]\s*热门(?:讨论|话题)', description)
    book_match = re.search(r'赠书\s*(\d+)\s*本', description)

    parts = []
    if article_count:
        parts.append(f"{article_count} article{'s' if article_count != 1 else ''}")
    if project_count:
        parts.append(f"{project_count} open-source project{'s' if project_count != 1 else ''}")
    if audio_video_match:
        count = int(audio_video_match.group(1))
        parts.append(f"{count} audio/video{'s' if count != 1 else ''}")
    if hot_topic_match:
        count = int(hot_topic_match.group(1))
        parts.append(f"{count} hot discussion{'s' if count != 1 else ''}")
    if book_match:
        count = int(book_match.group(1))
        parts.append(f"{count} book giveaway{'s' if count != 1 else ''}")
    if parts:
        return "Shared " + ", ".join(parts)
    return description

def replace_front_matter_field(content, field_name, new_value):
    """替换 front matter 中的单行字段，并尽量保留原始引号风格"""
    pattern = rf"^({field_name}:\s*['\"]?)(.*?)(['\"]?\s*)$"
    return re.sub(pattern, rf"\g<1>{new_value}\g<3>", content, count=1, flags=re.MULTILINE)

def split_and_generate_files(input_file, tmp_en_file):
    """
    分拆源文件的中英文标题，生成两份文件
    :param input_file: 输入文件路径（中英双语版）
    :param tmp_en_file: 输出文件路径（英文版）
    注：中文版会覆盖原始输入文件
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 定义二级标题的中英文对照表
    section_translations = {
        '🦄文章&教程': '🦄Articles & Tutorials',
        '🐿️项目&资源': '🐿️Projects & Resources',
        '🐢播客&视频': '🐢Podcasts & Videos',
        '🥂讨论&问题': '🥂Discussions & Questions',
        '🐧往年回顾': '🐧Past Issues'
    }

    # 查找所有markdown链接
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    matches = link_pattern.findall(content)

    # 分别处理中英文版本
    new_content1 = content  # 中文版
    new_content2 = content  # 英文版
    
    for text, url in matches:
        if '---' in text:  # 标题包含中英文分隔符
            parts = text.split('---', 1)
            new_text1 = parts[0]  # 中文部分
            new_text2 = parts[1] if len(parts) > 1 else ''  # 英文部分
            new_content1 = new_content1.replace(f'[{text}]({url})', f'[{new_text1}]({url})')
            new_content2 = new_content2.replace(f'[{text}]({url})', f'[{new_text2}]({url})')

    content_meta = get_front_matter(input_file) or {}
    weekly_no = extract_weekly_no(input_file)
    title = content_meta.get('title')
    if title:
        chinese_title, _ = split_bilingual_text(title)
        english_title = build_english_weekly_title(title, weekly_no)
        new_content1 = replace_front_matter_field(new_content1, 'title', chinese_title)
        new_content2 = replace_front_matter_field(new_content2, 'title', english_title)

    description = content_meta.get('description')
    if description:
        chinese_description, english_description = split_bilingual_text(description)
        english_description = english_description or build_english_description(chinese_description)
        new_content1 = replace_front_matter_field(new_content1, 'description', chinese_description)
        new_content2 = replace_front_matter_field(new_content2, 'description', english_description)
    
    # 处理二级标题的中英文转换
    for chinese_title, english_title in section_translations.items():
        # 匹配二级标题格式: ## [中文标题](url)
        chinese_pattern = rf'## \[{re.escape(chinese_title)}\]'
        english_replacement = f'## [{english_title}]'
        new_content2 = re.sub(chinese_pattern, english_replacement, new_content2)
        
        # 匹配粗体格式: **[中文标题](url)**
        chinese_bold_pattern = rf'\*\*\[{re.escape(chinese_title)}\]'
        english_bold_replacement = f'**[{english_title}]'
        new_content2 = re.sub(chinese_bold_pattern, english_bold_replacement, new_content2)

    # 保存处理后的文件
    with open(input_file, 'w', encoding='utf-8') as f1:
        f1.write(new_content1)
    
    with open(tmp_en_file, 'w', encoding='utf-8') as f2:
        f2.write(new_content2)

def read_md(file_path):
    """
    读取并解析markdown文件，返回内容二级标题及其子标题
    :param file_path: markdown文件路径
    :return: 字典，key为二级标题，value为其下的子标题列表
    注：只返回包含子标题的部分
    """
    with open(file_path, 'r', encoding="utf-8") as f:
        file_content = f.read()
        origin_content = parse_md(file_content)
        # 过滤掉没有子标题的部分
        new_content = {key: value for key, value in origin_content.items() if value}
        return new_content

def parse_md(file_content):
    """
    解析markdown文件内容，提取二级标题和其下的列表项
    :param file_content: markdown文件内容
    :return: 字典，key为二级标题，value为其下的列表项
    """
    # 提取所有二级标题
    titles = re.findall(r'## (.*?)\n', file_content)
    # 提取二级标题和列表项（带链接的形式）
    sub_titles = re.findall(r'## (.*?)\n|\d+、\[(.*?)\]\(.*?\)', file_content)

    # 初始化结果字典
    parsed_content = {title: [] for title in titles}

    # 遍历匹配结果，将列表项添加到对应的标题下
    current_title = None
    for title, sub_title in sub_titles:
        if title:  # 找到新的二级标题
            current_title = title
        elif current_title is not None and sub_title:  # 找到列表项
            parsed_content[current_title].append(sub_title.strip())

    return parsed_content

def content_to_string(contents):
    """
    将解析后的markdown内容转换为格式化的字符串
    :param contents: 包含标题和子标题的字典
    :return: 格式化后的字符串，每个标题下的列表项使用圆圈数字标记
    """
    message = ""
    for section, sub_sections in contents.items():
        if sub_sections:  # 只处理有子标题的部分
            message += f"**{section}**\n\n"
            for i, sub_section in enumerate(sub_sections, 1):
                message += f"{chr(9311 + i)} {sub_section}\n"
            message += "\n"
    return message

def get_front_matter(file_path):
    """
    解析Markdown文件的YAML元数据
    :param file_path: markdown文件路径
    :return: 元数据字典
    """
    with open(file_path, 'r', encoding="utf-8") as f:
        file_content = f.read()
        # 提取YAML元数据部分（位于文件开头的两个---之间）
        match = re.search(r'---\n(.*?)\n---', file_content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1))

def write_summary_content(f, content_meta, md_body, weekly_no, source_file=None, with_metadata=False, is_english=False):
    """
    写入摘要文件的内容
    :param f: 文件对象
    :param content_meta: 元数据字典
    :param md_body: 正文内容
    :param weekly_no: 期号
    :param source_file: 源文件路径，用于复制元数据
    :param with_metadata: 是否写入元数据
    :param is_english: 是否为英文版本
    """
    if with_metadata and source_file:
        # 从源文件复制完整的元数据
        with open(source_file, 'r', encoding='utf-8') as source:
            content = source.read()
            meta_match = re.search(r'---(.*?)---', content, re.DOTALL)
            if meta_match:
                f.write("---" + meta_match.group(1) + "---\n\n")
    else:
        # 只写入标题
        f.write(f"# {content_meta['title']}\n\n")
    
    # 根据语言版本选择对应的文本常量
    if is_english:
        intro = WEEKLY_INTRO_EN
        subscription_info = SUBSCRIPTION_INFO_EN
        season2_summary = SEASON2_SUMMARY_EN
        free_collection = FREE_COLLECTION_EN
        season1_summary = SEASON1_SUMMARY_EN
        summary_text = "Here are the title summaries for this issue:"
        full_text_info = f"After subscribing, you can view the full text of Issue {weekly_no} for free:"
    else:
        intro = WEEKLY_INTRO
        subscription_info = SUBSCRIPTION_INFO
        season2_summary = SEASON2_SUMMARY
        free_collection = FREE_COLLECTION
        season1_summary = SEASON1_SUMMARY
        summary_text = "以下是本期标题摘要："
        full_text_info = f"订阅后，可免费查看 第 {weekly_no} 期周刊的全文："
    
    # 写入正文内容
    f.write(intro + "\n\n")
    f.write(f"{content_meta['description']}\n\n")
    f.write(f"{summary_text} \n\n")

    # 添加换行符，解决某些平台无法正确换行的问题
    formatted_body = md_body
    for i in range(1, 20):
        formatted_body = formatted_body.replace(chr(9311 + i), "\n" + chr(9311 + i))
    f.write(formatted_body + "\n\n")
    
    # 写入订阅信息和其他固定内容
    f.write(subscription_info + "\n\n")
    f.write(f"{full_text_info} \n\n")
    f.write(season2_summary + "\n\n")
    f.write(free_collection + "\n\n")
    f.write(season1_summary + "\n\n")
    
    # 中文版才显示微信二维码
    if not is_english:
        f.write(WECHAT_QR + "\n\n")

def write_to_md_file(weekly_no, content_meta, md_body, pub_date, weekly_file):
    """
    生成两个版本的摘要文件：
    1. 博客版本：使用完整版的元数据，但内容是摘要
    2. Github版本：仅保留title和pubDate元数据，内容是摘要
    :param weekly_no: 期号
    :param content_meta: 元数据字典
    :param md_body: 正文内容
    :param pub_date: 发布日期
    :param weekly_file: 周刊文件路径
    """
    # 1. 生成博客版本（完整元数据+摘要内容）
    blog_dir = os.path.expanduser('~/Documents/GitHub/astro-blog/src/pages/posts')
    if not os.path.exists(blog_dir):
        os.makedirs(blog_dir)
    
    blog_file = os.path.join(blog_dir, f"{pub_date}-weekly.md")
    if not os.path.exists(blog_file):
        print("Writing blog version summary...")
        with open(blog_file, 'w', encoding="utf-8") as f:
            write_summary_content(f, content_meta, md_body, weekly_no, weekly_file, True)
    
    # 2. 生成Github版本（简化元数据+摘要内容）
    print("Writing github version summary...")
    with open(weekly_file, 'w', encoding='utf-8') as f:
        write_summary_content(f, content_meta, md_body, weekly_no)

def write_to_md_file_en(weekly_no, pub_date, en_weekly_file):
    """
    生成英文版摘要文件，用于发布到Medium、Dev.to等英文博客平台
    :param weekly_no: 期号
    :param pub_date: 发布日期
    :param en_weekly_file: 英文周刊文件路径
    """
    # 从英文版文件中读取真正的内容和元数据
    if os.path.exists(en_weekly_file):
        en_content_meta = get_front_matter(en_weekly_file)
        en_content_body = content_to_string(read_md(en_weekly_file))
    else:
        print(f"Warning: English weekly file not found: {en_weekly_file}")
        return None

    if en_content_meta:
        en_content_meta['title'] = build_english_weekly_title(en_content_meta.get('title', ''), weekly_no)
        en_content_meta['description'] = build_english_description(en_content_meta.get('description', ''))
    
    # 生成英文版摘要文件
    en_summary_dir = 'docs/en'
    if not os.path.exists(en_summary_dir):
        os.makedirs(en_summary_dir)
    
    en_summary_file = os.path.join(en_summary_dir, f"{pub_date}-weekly.md")
    print("Writing English version summary...")
    with open(en_summary_file, 'w', encoding='utf-8') as f:
        write_summary_content(f, en_content_meta, en_content_body, weekly_no, is_english=True)
    
    return en_summary_file, en_content_meta

def set_title(no):
    """
    生成Telegram消息的标题部分
    :param no: 期号
    :return: 格式化的标题字符串
    """
    tag = "#Python潮流周刊 \n\n"
    title = f"🐱🐱🐱🐱  第 {no} 期  🐱🐱🐱🐱\n\n"
    return tag + title

def set_content_body(file_path, weekly_no, pub_date):
    """
    生成并返回消息的正文部分，同时生成摘要文件
    :param file_path: 周刊文件路径
    :param weekly_no: 期号
    :param pub_date: 发布日期
    :return: 格式化的正文内容
    """
    content_meta = get_front_matter(file_path)
    content_body = content_to_string(read_md(file_path))
    # 在非在线环境下生成摘要文件
    online_action = os.getenv('ONLINE_ACTION')
    if not online_action:
        write_to_md_file(weekly_no, content_meta, content_body, pub_date, file_path)
    return content_body

def set_footer():
    """
    返回Telegram消息的页脚部分
    :return: 订阅信息文本
    """
    return FOOTER_SUBSCRIPTION

def set_channel():
    """
    返回Telegram频道信息
    :return: 频道信息文本
    """
    return "🐱频道 @pythontrendingweekly"

async def send_to_telegram(bot_token, chat_id, text, image_path=None):
    """
    发送消息到Telegram频道
    :param bot_token: Telegram机器人token
    :param chat_id: 目标频道ID
    :param text: 消息文本
    :param image_path: 可选的图片路径
    """
    print("Sending content to tg bot")
    bot = Bot(token=bot_token)
    if image_path:
        with open(image_path, 'rb') as f:
            await bot.send_photo(chat_id=chat_id, photo=InputFile(f), caption=text, parse_mode='Markdown')
    else:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown', disable_web_page_preview=True)

def extract_weekly_no(file_path):
    """
    从文件内容中提取期号
    :param file_path: 周刊文件路径
    :return: 期号字符串
    """
    print(f"Extracting weekly number from {file_path}")
    with open(file_path, 'r', encoding="utf-8") as f:
        content = f.read()
        # 用正则从 title 字段提取期号，不依赖行号
        match = re.search(r"title:\s*['\"][^'\"]*?#(\d+)", content)
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid weekly no format: could not find issue number in title")

def get_message(weekly_no, content_body):
    """
    组装完整的Telegram消息
    :param weekly_no: 期号
    :param content_body: 正文内容
    :return: 完整的消息文本
    """
    print("Getting weekly message")
    header = set_title(weekly_no)
    footer = set_footer()
    channel = set_channel()
    return header + content_body + footer + channel

def count_words(file_path):
    """
    统计markdown文件的字数
    :param file_path: 文件路径
    :return: 字数统计
    注：不包括链接URL和元数据部分
    """
    print("Counting words in the file...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除markdown的元数据
    content = re.sub(r'---.*?---', '', content, flags=re.DOTALL)
    
    # 保留链接文本，移除URL
    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
    
    # 移除其他markdown标记
    content = re.sub(r'[#*`>]', '', content)  # 移除#、*、`、>等markdown标记
    content = re.sub(r'\n+', '\n', content)   # 将多个换行符替换为单个
    
    # 使用jieba进行分词
    words = jieba.lcut(content)
    # 过滤掉空白字符和标点符号
    words = [word for word in words if word.strip()]
    
    return len(words)

def update_word_count(file_path, word_count):
    """
    更新文件中的字数统计
    :param file_path: 文件路径
    :param word_count: 字数统计结果
    """
    print("Updating word count in the file...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式替换字数，同时处理有数字和无数字的情况
    updated_content = re.sub(r'全文(\s*?)(\d+)?(\s*?)字', f'全文 {word_count} 字', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

def copy_to_archive(source_file, pub_date):
    """
    复制中文完整版到项目归档目录
    :param source_file: 源文件路径
    :param pub_date: 发布日期
    :param weekly_no: 期号
    """
    # 获取项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    ebook_dir = os.path.join(project_root, 'docs', 'tmp')
    if not os.path.exists(ebook_dir):
        os.makedirs(ebook_dir)
    ebook_target = os.path.join(ebook_dir, f'{pub_date}-weekly.md')
    print(f"Copying Chinese version to project archive directory: {ebook_target}")
    shutil.copy2(source_file, ebook_target)

def update_readme(weekly_no, zh_weekly_file, zh_content_meta, en_weekly_file=None, en_content_meta=None):
    """
    更新README文件，在往期列表部分添加新的周刊链接
    :param weekly_no: 期号
    :param zh_weekly_file: 中文周刊路径
    :param zh_content_meta: 中文元数据
    :param en_weekly_file: 英文周刊路径
    :param en_content_meta: 英文元数据
    """
    print("Updating README files...")

    if not zh_content_meta:
        print("Warning: Could not find Chinese metadata for weekly file")
        return

    zh_title, _ = split_bilingual_text(extract_issue_title(zh_content_meta['title']))
    zh_description, _ = split_bilingual_text(zh_content_meta['description'])
    
    # 更新中文README
    update_single_readme('README_ZH.md', zh_description,
                        "## 🦄往期列表\n\n", f"- 第 {weekly_no} 期：[{zh_title}](./{zh_weekly_file})\n")
    
    # 更新英文README
    if en_weekly_file and en_content_meta:
        en_title = extract_issue_title(en_content_meta['title'])
        update_single_readme('README.md', en_content_meta['description'],
                            "## 🦄 Past Issues\n\n", f"- Issue {weekly_no}: [{en_title}](./{en_weekly_file})\n")

def update_single_readme(readme_file, description, section_start, entry_format):
    """
    更新单个README文件
    :param readme_file: README文件路径
    :param description: 描述
    :param section_start: 往期列表部分的开始标记（如 "## 🦄往期列表"）
    :param entry_format: 条目格式
    """
    try:
        # 读取README文件
        with open(readme_file, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        # 生成新的周刊条目（确保以换行结尾）
        new_entry = entry_format
        new_entry += f"  - {description}\n"
        
        # 用正则匹配往期列表标题行（兼容不同换行符和前导空格）
        # 提取纯标题文本用于匹配，去掉末尾的 \n\n
        heading_text = section_start.rstrip('\n')
        pattern = re.compile(r'^(' + re.escape(heading_text) + r')\s*\n+', re.MULTILINE)
        match = pattern.search(readme_content)
        
        if match:
            # 在标题行及其后续空行之后插入新条目
            insert_pos = match.end()
            # 确保标题后有两个换行
            updated_content = readme_content[:insert_pos].rstrip('\n') + '\n\n' + new_entry + readme_content[insert_pos:].lstrip('\n')
            
            # 写入更新后的内容
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                print(f"{readme_file} updated successfully!")
        else:
            print(f"Warning: Could not find past issues section in {readme_file}")
    except FileNotFoundError:
        print(f"Warning: {readme_file} not found")
    except Exception as e:
        print(f"Error updating {readme_file}: {e}")

def _scan_weekly_issues():
    """扫描 docs/ 下所有周刊文件，返回 [(date_str, issue_no), ...] 按日期升序。"""
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
    weekly_files = sorted(
        f for f in os.listdir(docs_dir)
        if re.match(r'\d{4}-\d{2}-\d{2}-weekly\.md$', f)
    )
    issues = []
    for i, fname in enumerate(weekly_files, 1):
        m = re.match(r'(\d{4}-\d{2}-\d{2})-weekly\.md$', fname)
        if m:
            issues.append((m.group(1), i))
    return issues


def _find_issue_date(issue_no, issues):
    """根据期数查找对应日期。"""
    for date_str, num in issues:
        if num == issue_no:
            return date_str
    return None


def _strip_frontmatter_for_github(content):
    """去掉 Astro 专用 frontmatter 字段，只保留 title 和 pubDate。"""
    lines = content.split('\n')
    if not lines or lines[0].strip() != '---':
        return content

    # 找到 frontmatter 结束位置
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break
    if end_idx is None:
        return content

    fm_lines = lines[1:end_idx]
    body_lines = lines[end_idx + 1:]

    # 只保留 title 和 pubDate
    keep_fields = {'title', 'pubDate'}
    new_fm = []
    for line in fm_lines:
        key = line.split(':')[0].strip() if ':' in line else ''
        if key in keep_fields:
            new_fm.append(line)

    result = ['---'] + new_fm + ['---', ''] + body_lines
    return '\n'.join(result)


def disclose_full_issue(weekly_no):
    """公开处理 N-50 期：将归档全文替换正式目录的简化版。

    检查 docs/tmp/ 中是否有第 N-50 期的全文版，若有则：
    1. 中文：提取全文，去掉 Astro 专用 frontmatter，覆盖 docs/
    2. 英文：若 docs/en/tmp/ 有全文，覆盖 docs/en/
    3. astro-blog：用完整 frontmatter 的全文覆盖博客简化版
    4. 清理 tmp 归档文件
    """
    target_no = int(weekly_no) - 50
    if target_no < 1:
        return

    issues = _scan_weekly_issues()
    target_date = _find_issue_date(target_no, issues)
    if not target_date:
        return

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 1. 中文全文：docs/tmp/ → docs/
    tmp_zh = os.path.join(project_root, 'docs', 'tmp', f'{target_date}-weekly.md')
    docs_zh = os.path.join(project_root, 'docs', f'{target_date}-weekly.md')

    if os.path.exists(tmp_zh) and os.path.exists(docs_zh):
        full_content = open(tmp_zh, encoding='utf-8').read()
        # GitHub 版只保留 title + pubDate
        github_content = _strip_frontmatter_for_github(full_content)
        with open(docs_zh, 'w', encoding='utf-8') as f:
            f.write(github_content)
        print(f"  ✓ 中文全文已公开: docs/{target_date}-weekly.md")

        # 3. astro-blog：保留完整 frontmatter
        blog_dir = os.path.expanduser('~/Documents/GitHub/astro-blog/src/pages/posts')
        blog_file = os.path.join(blog_dir, f'{target_date}-weekly.md')
        if os.path.exists(blog_dir):
            with open(blog_file, 'w', encoding='utf-8') as f:
                f.write(full_content)
            print(f"  ✓ astro-blog 已同步: {target_date}-weekly.md")

        # 清理 tmp 中文归档
        os.remove(tmp_zh)
        print(f"  ✓ 已清理: docs/tmp/{target_date}-weekly.md")
    else:
        if os.path.exists(docs_zh):
            # 正式目录已是全文版（之前公开过），跳过
            pass

    # 2. 英文全文：docs/en/tmp/ → docs/en/
    tmp_en = os.path.join(project_root, 'docs', 'en', 'tmp', f'{target_date}-weekly.md')
    docs_en = os.path.join(project_root, 'docs', 'en', f'{target_date}-weekly.md')

    if os.path.exists(tmp_en) and os.path.exists(docs_en):
        shutil.copy2(tmp_en, docs_en)
        print(f"  ✓ 英文全文已公开: docs/en/{target_date}-weekly.md")
        os.remove(tmp_en)
        print(f"  ✓ 已清理: docs/en/tmp/{target_date}-weekly.md")


def process_weekly(pub_date=None):
    """
    处理周刊的主函数
    :param pub_date: 可选的发布日期，默认为当天
    处理流程：
    1. 拆分中英文版本（英文版自动保存到tmp目录，中文版覆盖原文件）
    2. 统计中文版字数并更新
    3. 复制中文版到项目归档目录
    4. 生成中文版摘要文件（博客版和Github版）
    5. 生成英文版摘要文件
    6. 用已生成的中英摘要元数据更新 README
    7. 发送消息版到Telegram
    8. 自动公开 N-50 期全文（检测并替换 docs/ + astro-blog）
    9. 自动调用 weekly_save_count.py 刷新统计数据库
    """
    if pub_date is None:
        pub_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    weekly_file = f'docs/{pub_date}-weekly.md'
    tmp_en_file = f'docs/en/tmp/{pub_date}-weekly.md'
    en_summary_file = f'docs/en/{pub_date}-weekly.md'
    
    if not os.path.exists(weekly_file):
        print(f"File {weekly_file} does not exist.")
        sys.exit(1)

    original_content_meta = get_front_matter(weekly_file)
    weekly_no = extract_weekly_no(weekly_file)

    # 1. 拆分中英文版本
    print("1. Splitting Chinese and English versions...")
    split_and_generate_files(weekly_file, tmp_en_file)
    
    # 2. 统计中文版字数并更新
    print("2. Counting words and updating...")
    word_count = count_words(weekly_file)
    update_word_count(weekly_file, word_count)
    
    # 3. 复制完整版文件到归档目录
    print("3. Copying files to archive...")
    copy_to_archive(weekly_file, pub_date)
    
    # 4. 生成中文版周刊摘要
    print("4. Generating Chinese summary files...")
    content_meta = get_front_matter(weekly_file)
    content_body = content_to_string(read_md(weekly_file))
    write_to_md_file(weekly_no, content_meta, content_body, pub_date, weekly_file)
    
    # 5. 生成英文版周刊摘要
    print("5. Generating English blog summary...")
    en_content_meta = None
    if os.path.exists(tmp_en_file):
        en_summary_file, en_content_meta = write_to_md_file_en(weekly_no, pub_date, tmp_en_file)
        print(f"English blog summary generated: {en_summary_file}")
    else:
        print("Warning: English version file not found, skipping English summary generation.")

    # 6. 更新 README（使用已生成的中英周刊元数据）
    print("6. Updating README files...")
    update_readme(weekly_no, weekly_file, original_content_meta, en_summary_file, en_content_meta)

    # 7. 生成中文版摘要消息并发送到Telegram
    print("7. Generating Chinese summary and sending to Telegram...")
    message = get_message(weekly_no, content_body)
    tg_bot_token = os.environ['TG_BOT_TOKEN']
    tg_chat_id = os.environ['TG_CHAT_ID']
    image_path = "resources/img/python-weekly.png"
    asyncio.run(send_to_telegram(tg_bot_token, tg_chat_id, message, image_path))

    # 8. 自动公开 N-50 期全文（归档全文 → 替换正式目录简化版 + 同步 astro-blog）
    print(f"\n8. Disclosing full issue #{int(weekly_no) - 50} (N-50)...")
    disclose_full_issue(weekly_no)

    # 9. 刷新统计数据库与 stats.json
    print("\n9. Updating weekly statistics (weekly_save_count)...")
    save_count_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'weekly_save_count.py'
    )
    import subprocess
    result = subprocess.run(
        [sys.executable, save_count_script],
        capture_output=True, text=True, timeout=60,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    if result.returncode == 0:
        print(result.stdout.strip() or "  ✓ 统计已更新")
    else:
        print(f"  ⚠️ weekly_save_count 失败: {result.stderr.strip()}")

    print("Weekly processing completed!")
    print("Files generated:")
    print(f"  - Chinese version: {weekly_file}")
    print(f"  - English version: {tmp_en_file}")
    if os.path.exists(tmp_en_file):
        print(f"  - English summary: docs/en/summary/{pub_date}-weekly-summary.md")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_weekly(sys.argv[1])
    else:
        process_weekly()
