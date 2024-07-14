import re
import os
from datetime import datetime

def is_within_date_range(filename, start_date, end_date):
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})-weekly\.md', filename)
    if date_match:
        file_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
        return start_date <= file_date <= end_date
    return False

def process_files_in_directory(directory, season, file_name):
    files = [f for f in os.listdir(directory) if f.endswith('weekly.md')]
    files = [f for f in files if is_within_date_range(f, season[0], season[1])]
    files.sort(key=lambda x: datetime.strptime(re.search(r'(\d{4}-\d{2}-\d{2})', x).group(1), '%Y-%m-%d'))

    for filename in files:
        full_path = os.path.join(directory, filename)
        content = extract_content(full_path)
        write_new_markdown(content, file_name)

def extract_issue_title(lines):
    issue_title_regex = re.compile(r'#(\d+)：(.+)')
    for _, line in enumerate(lines[:3]):
        match = issue_title_regex.search(line)
        if match:
            return "## {} {} \n\n".format(match.group(1), match.group(2).rstrip('\''))
    return None

def process_section(lines, header_regex):
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
    full_output_path = os.path.join(current_dir, output_file_name)
    with open(full_output_path, 'a', encoding='utf-8') as file:
        file.writelines(new_content)

current_dir = os.path.dirname(os.path.realpath(__file__))
season_1 = (datetime(2023, 5, 13), datetime(2023, 12, 9))
process_files_in_directory(current_dir, season_1, "season_1.md")
season_2 = (datetime(2023, 12, 16), datetime(2024, 7, 13))
process_files_in_directory(current_dir, season_2, "season_2.md")