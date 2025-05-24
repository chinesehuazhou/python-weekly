"""
这个脚本用于将Python周刊的单期文章合并成季度合集。
它会根据文件名中的日期将指定时间范围内的周刊文章进行提取和合并，
生成新的Markdown文件作为季度合集。

主要功能：
1. 按日期范围筛选周刊文件
2. 提取每期周刊的关键内容
3. 保持原有的文章分类结构
4. 生成带有原文链接的合集文档
"""

import re
import os
from datetime import datetime

def is_within_date_range(filename, start_date, end_date):
    """
    判断文件名中的日期是否在指定的日期范围内
    
    Args:
        filename (str): 文件名，格式应为'YYYY-MM-DD-weekly.md'
        start_date (datetime): 起始日期
        end_date (datetime): 结束日期
    
    Returns:
        bool: 如果文件日期在范围内返回True，否则返回False
    """
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})-weekly\.md', filename)
    if date_match:
        file_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
        return start_date <= file_date <= end_date
    return False

def process_files_in_directory(directory, season, file_name):
    """
    处理指定目录下的所有周刊文件，将符合日期范围的文件内容合并
    
    Args:
        directory (str): 要处理的目录路径
        season (tuple): 包含开始和结束日期的元组 (start_date, end_date)
        file_name (str): 输出的合集文件名
    """
    files = [f for f in os.listdir(directory) if f.endswith('weekly.md')]
    files = [f for f in files if is_within_date_range(f, season[0], season[1])]
    files.sort(key=lambda x: datetime.strptime(re.search(r'(\d{4}-\d{2}-\d{2})', x).group(1), '%Y-%m-%d'))

    for filename in files:
        full_path = os.path.join(directory, filename)
        content = extract_content(full_path)
        write_new_markdown(content, file_name)

def extract_issue_title(lines):
    """
    从文件内容中提取期号和标题
    
    Args:
        lines (list): 文件内容的行列表
    
    Returns:
        str: 格式化后的标题，如果未找到则返回None
    """
    issue_title_regex = re.compile(r'#(\d+)：(.+)')
    for _, line in enumerate(lines[:3]):
        match = issue_title_regex.search(line)
        if match:
            return "## {} {} \n\n".format(match.group(1), match.group(2).rstrip('\''))
    return None

def process_section(lines, header_regex):
    """
    处理文章的各个分类部分（如文章&教程、项目&资源等）
    
    Args:
        lines (list): 文件内容的行列表
        header_regex (Pattern): 用于匹配分类标题的正则表达式
    
    Returns:
        list: 处理后的内容列表，包含调整后的标题层级
    """
    collecting = False
    section_content = []
    new_content = []
    for line in lines:
        header_match = header_regex.match(line)
        if header_match:
            if collecting:
                new_content.extend(section_content)
                section_content = []
            collecting = True
            section_content.append(line.replace('## ', '### '))
        elif collecting:
            if line.startswith('## '):
                new_content.extend(section_content)
                section_content = []
                collecting = False
            else:
               section_content.append(line)
    if collecting:
        new_content.extend(section_content)
    return new_content

def extract_content(file_path):
    """
    从单个周刊文件中提取内容
    
    Args:
        file_path (str): 周刊文件的路径
    
    Returns:
        list: 提取并格式化后的内容列表，包含标题、原文链接和分类内容
    """
    full_path = os.path.join(current_dir, file_path)
    filename = os.path.basename(file_path)
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})-weekly\.md', filename)
    date = date_match.group(1)

    with open(full_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    title = extract_issue_title(lines)
    blog_and_date = f"[博客原文](https://pythoncat.top/posts/{date}-weekly) | 发布时间：{date}\n\n"
    new_content = [title, blog_and_date]

    sub_title_regex = re.compile(r'^##.*?(文章&教程|项目&资源|播客&视频|讨论&问题|往年回顾).*$')
    new_content.extend(process_section(lines, sub_title_regex))

    return new_content

def write_new_markdown(new_content, output_file_name):
    """
    将处理后的内容写入新的Markdown文件
    
    Args:
        new_content (list): 要写入的内容列表
        output_file_name (str): 输出文件名
    """
    full_output_path = os.path.join(current_dir, output_file_name)
    with open(full_output_path, 'a', encoding='utf-8') as file:
        file.writelines(new_content)

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.realpath(__file__))

# 定义第一季度的日期范围（2023.5.13 - 2023.12.9）
season_1 = (datetime(2023, 5, 13), datetime(2023, 12, 9))
process_files_in_directory(current_dir, season_1, "season_1.md")

# 定义第二季度的日期范围（2023.12.16 - 2024.7.13）
season_2 = (datetime(2023, 12, 16), datetime(2024, 7, 13))
process_files_in_directory(current_dir, season_2, "season_2.md")

season_3 = (datetime(2024, 7, 20), datetime(2025, 2, 23))
process_files_in_directory(current_dir, season_3, "season_3.md")