import asyncio
import datetime
import os
import re
import sys
import yaml
from dotenv.main import load_dotenv
from telegram import Bot, InputFile

if not os.getenv('TG_BOT_TOKEN') or not os.getenv('TG_CHAT_ID'):
    load_dotenv()


def read_md(file_path):
    """
    解析markdown文件，返回内容二级标题及其子标题；不含子标题为空的部分
    :param file_path: md文件
    :return: 内容摘要的字典
    """
    with open(file_path, 'r', encoding="utf-8") as f:
        file_content = f.read()
        origin_content = parse_md(file_content)
        new_content = {key: value for key, value in origin_content.items() if value}
        return new_content


def parse_md(file_content):
    """
    解析markdown文件，返回内容二级标题及其子标题
    :param file_content: md文件内容
    :return: 内容摘要的字典
    """
    titles = re.findall(r'## (.*?)\n', file_content)
    sub_titles = re.findall(r'## (.*?)\n|\d、\[(.*?)\]\(.*?\)', file_content)

    parsed_content = {title: [] for title in titles}

    current_title = None
    for title, sub_title in sub_titles:
        if title:
            current_title = title
        elif current_title is not None:
            parsed_content[current_title].append(sub_title.strip())

    return parsed_content


def content_to_string(contents):
    message = ""
    for section, sub_sections in contents.items():
        if sub_sections:
            message += "**" + section + "** \n\n"
            for i, sub_section in enumerate(sub_sections, start=1):
                message += f"{chr(9311 + i)} " + sub_section + "\n"
            message += "\n"
    return message


def get_front_matter(file_path):
    """
    解析Markdown文件的元数据，返回成字典
    """
    with open(file_path, 'r', encoding="utf-8") as f:
        file_content = f.read()
        match = re.search(r'---\n(.*?)\n---', file_content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1))


def write_to_md_file(weekly_no, content_meta, md_body):
    """
    将内容写入到markdown文件中
    :param content_meta: Markdown元数据
    :param md_body: Markdown主体内容
    """
    file_name = f"Python 潮流周刊第 {weekly_no} 期"
    if os.path.exists(file_name + ".md"):
        return
    print("Writing summary to local file")
    with open(file_name + ".md", 'w', encoding="utf-8") as f:
        f.write(f"# {content_meta['title']}\n\n")
        f.write("本周刊由 Python猫 出品，精心筛选国内外的 250+ 信息源，"
                "为你挑选最值得分享的文章、教程、开源项目、软件工具、播客和视频、热门话题等内容。"
                "愿景：帮助所有读者精进 Python 技术，并增长职业和副业的收入。\n\n")
        f.write(f"{content_meta['description']}\n\n")
        f.write("以下是本期摘要： \n\n")

        # 添加换行符，解决某些平台无法正确换行的问题
        for i in range(1, 20):
            md_body = md_body.replace(chr(9311 + i), "\n" + chr(9311 + i))
        f.write(md_body + "\n\n")
        f.write(f"[本期正文 xxx 字，点击阅读（付费链接）]()\n\n")
        f.write("**微信关注 Python猫**：[https://img.pythoncat.top/python_cat.jpg](https://img.pythoncat.top/python_cat.jpg) \n\n")


def set_title(no):
    tag = "#Python潮流周刊 \n\n"
    title = f"🐱🐱🐱🐱  第 {no} 期  🐱🐱🐱🐱\n\n"
    return tag + title


def set_content_body(file_path, weekly_no):
    content_meta = get_front_matter(file_path)
    content_body = content_to_string(read_md(file_path))
    online_action = os.getenv('ONLINE_ACTION')
    if not online_action:
        write_to_md_file(weekly_no, content_meta, content_body)
    return content_body


def set_footer():
    read_all = "周刊实行付费订阅制，年费128元，预计50期，超过10万字。现在订阅，每周让自己进步一点点。\n\n"
    read_all += f"👀 [订阅方式一（小报童）](https://xiaobot.net/p/python_weekly) \n\n"
    read_all += f"👀 [订阅方式二（爱发电）](https://afdian.net/a/python_weekly) \n\n"
    read_all += f"👀 [想详细了解周刊](https://pythoncat.top/posts/2024-05-06-information-gap) \n\n"
    return read_all


def set_channel():
    return "🐱频道 @pythontrendingweekly"


async def send_to_telegram(bot_token, chat_id, text, image_path=None):
    """
    发送消息到Telegram
    :param bot_token: 机器人的API令牌
    :param chat_id: 聊天的ID
    :param text: 要发送的文本消息
    :param image_path: 要发送的图片的路径
    """
    print("Sending content to tg bot")
    bot = Bot(token=bot_token)
    if image_path:
        with open(image_path, 'rb') as f:
            await bot.send_photo(chat_id=chat_id, photo=InputFile(f), caption=text, parse_mode='Markdown')
    else:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown', disable_web_page_preview=True)


def extract_weekly_no(file_path):
    """默认文件第二行或第三行为标题，解析期数"""
    print(f"Extracting weekly number from {file_path}")
    with open(file_path, 'r', encoding="utf-8") as f:
        lines = f.readlines()
        match = re.search(r'#(\d+)', lines[1])
        if match:
            return match.group(1)
        match = re.search(r'#(\d+)', lines[2])
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid weekly no format in the second line.")


def get_message(file_path, weekly_no):
    print("Getting weekly message")
    header = set_title(weekly_no)
    content_body = set_content_body(file_path, weekly_no)
    footer = set_footer()
    channel = set_channel()
    return header + content_body + footer + channel


def main():
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    current_date = '2024-07-13'
    file_name = f"{current_date}-weekly"
    file_path = os.path.join("docs", f"{file_name}.md")
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        sys.exit(1)

    weekly_no = extract_weekly_no(file_path)
    message = get_message(file_path, weekly_no)

    tg_bot_token = os.environ['TG_BOT_TOKEN']
    tg_chat_id = os.environ['TG_CHAT_ID']
    image_path = "resources/img/python-weekly.jpg"
    asyncio.run(send_to_telegram(tg_bot_token, tg_chat_id, message, image_path))


main()
