import datetime
import os
import re
import sys


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


def write_to_md_file(weekly_no, md_body, url):
    """
    将内容写入到markdown文件中
    :param content: 要写入的内容
    :param file_name: md文件名
    """
    file_name = f"Python 潮流周刊第 {weekly_no} 期（摘要）"
    if os.path.exists(file_name + ".md"):
        return
    print("Writing summary to local file")
    with open(file_name + ".md", 'w', encoding="utf-8") as f:
        f.write(f"# {file_name}\n\n")
        f.write("本周刊由 Python猫 出品，精心筛选国内外的 250+ 信息源，"
                "为你挑选最值得分享的文章、教程、开源项目、软件工具、播客和视频、热门话题等内容。"
                "愿景：帮助所有读者精进 Python 技术，并增长职业和副业的收入。\n\n")
        f.write(f"周刊全文：{url} \n\n")
        f.write("以下是本期摘要： \n\n")

        # 添加换行符，解决某些平台无法正确换行的问题
        for i in range(1, 20):
            md_body = md_body.replace(chr(9311 + i), "\n" + chr(9311 + i))
        f.write(md_body + "\n\n")

        f.write(f"**查看全文**：{url} \n\n")
        f.write("**微信订阅**：https://img.pythoncat.top/python_cat.jpg \n\n")
        f.write("**邮箱订阅**：https://pythoncat.substack.com")


def main():
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    file_name = f"{current_date}-weekly"
    file_path = os.path.join("docs", f"{file_name}.md")
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        sys.exit(1)


main()
