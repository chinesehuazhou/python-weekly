"""
本脚本用于处理 Python 潮流周刊的 markdown 文件内容。
主要功能是提取并整理文章条目，按类别组织内容并生成结构化的摘要输出。
"""

import re

def extract_entries(filename, output_file):
    """
    从 markdown 文件中提取条目并按类别整理。
    
    参数说明：
        filename (str): 输入的 markdown 文件路径
        output_file (str): 整理后的输出文件保存路径
        
    处理流程：
    1. 读取 markdown 文件内容
    2. 将内容分割为章节和子章节
    3. 提取条目及其类别
    4. 收集附录中的链接
    5. 将整理后的内容写入输出文件
    """
    # 读取输入文件
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按 '## ' 分割内容为主要章节
    sections = re.split(r'^## ', content, flags=re.MULTILINE)[1:]
    
    # 初始化数据结构
    result = {}  # 存储按类别分类的主要条目
    appendix = []  # 存储带链接的附录条目
    
    # 处理每个章节
    for section in sections:
        # 按 '### ' 分割章节为子章节
        subsections = re.split(r'^### ', section, flags=re.MULTILINE)
        
        # 处理每个子章节
        for subsection in subsections[1:]:
            lines = subsection.strip().split('\n')
            # 提取类别名称，移除 markdown 链接格式
            category = re.sub(r'\[([^\]]+)\](?:\([^\)]+\))', r'\1', lines[0].strip())
            # 查找子章节中的所有编号条目
            entries = re.findall(r'^\d+、.*?(?=^\d+、|\Z)', subsection, flags=re.MULTILINE | re.DOTALL)
            
            # 如果类别不存在则初始化
            if category not in result:
                result[category] = []
            
            # 处理每个条目
            for entry in entries:
                # 提取主条目标题（编号后的内容）
                title_match = re.match(r'^\d+、(.*?)$', entry.split('\n')[0])
                if title_match:
                    main_entry = title_match.group(1).strip()
                    result[category].append(main_entry)
                
                # 提取附录条目（以"附"开头的括号内容）
                appendix_items = re.findall(r'（附.*?）', entry)
                for item in appendix_items:
                    # 从附录条目中提取 markdown 链接
                    links = re.findall(r'\[(.*?)\]\((.*?)\)', item)
                    appendix.extend([f"[{text}]({url})" for text, url in links])
    
    # 将整理后的内容写入输出文件
    with open(output_file, 'w', encoding='utf-8') as out:
        # 按类别写入主要条目
        for category, entries in result.items():
            if entries:
                out.write(f"## {category}\n\n")
                for i, entry in enumerate(entries, 1):
                    out.write(f"{i}、{entry}\n\n")
                out.write('\n')
        
        # 如果存在附录则写入附录部分
        if appendix:
            out.write("## 附录\n")
            for i, item in enumerate(appendix, 1):
                out.write(f"{i}、{item}\n\n")
            out.write('\n')

if __name__ == '__main__':
    extract_entries('docs/season3_full.md', 'output_link_3.md')
