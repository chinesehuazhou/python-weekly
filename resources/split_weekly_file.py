import re

def split_and_generate_files(input_file, output_file):
    """
    分拆源文件的中英文标题，生成两份文件
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    matches = link_pattern.findall(content)

    new_content1 = content
    new_content2 = content
    for text, url in matches:
        if '---' in text:
            parts = text.split('---', 1)
            new_text1 = parts[0]
            new_text2 = parts[1] if len(parts) > 1 else ''
            new_content1 = new_content1.replace(f'[{text}]({url})', f'[{new_text1}]({url})')
            new_content2 = new_content2.replace(f'[{text}]({url})', f'[{new_text2}]({url})')

    with open(input_file, 'w', encoding='utf-8') as f1:
        f1.write(new_content1)
    
    with open(output_file, 'w', encoding='utf-8') as f2:
        f2.write(new_content2)


pub_date = '2024-12-21'
weekly_file = f'docs/{pub_date}-weekly.md'
output_file = f'resources/{pub_date}-weekly.md'
split_and_generate_files(weekly_file, output_file)
