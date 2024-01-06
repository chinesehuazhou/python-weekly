import re


def convert_to_markdown_link(title):
    match = re.match(r"## 第(\d+)期（(\d+-\d+-\d+)）", title)
    if match:
        issue_number = match.group(1)
        date = match.group(2)
        markdown_link = f"## [第{issue_number}期（{date}）](https://pythoncat.top/posts/{date}-weekly)"
        return markdown_link
    else:
        return title


def process_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

        # 使用正则表达式匹配所有二级标题
        pattern = r"## .*"
        matches = re.findall(pattern, content)

        # 对每个匹配到的标题进行替换
        for match in matches:
            converted_title = convert_to_markdown_link(match)
            content = content.replace(match, converted_title)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


markdown_file_path = 'path/to/2023-12-11-weekly.md'
process_markdown_file(markdown_file_path)
