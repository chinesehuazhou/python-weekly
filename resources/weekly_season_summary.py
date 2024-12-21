import re

def extract_entries(filename, output_file):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = re.split(r'^## ', content, flags=re.MULTILINE)[1:]
    
    result = {}
    appendix = []
    
    for section in sections:
        subsections = re.split(r'^### ', section, flags=re.MULTILINE)
        for subsection in subsections[1:]:
            lines = subsection.strip().split('\n')
            category = re.sub(r'\[([^\]]+)\](?:\([^\)]+\))', r'\1', lines[0].strip())
            entries = re.findall(r'^\d+、.*?(?=^\d+、|\Z)', subsection, flags=re.MULTILINE | re.DOTALL)
            
            if category not in result:
                result[category] = []
            
            for entry in entries:
                # 提取主条目（小标题）
                title_match = re.match(r'^\d+、(.*?)$', entry.split('\n')[0])
                if title_match:
                    main_entry = title_match.group(1).strip()
                    result[category].append(main_entry)
                
                # 提取附录条目
                appendix_items = re.findall(r'（附.*?）', entry)
                for item in appendix_items:
                    links = re.findall(r'\[(.*?)\]\((.*?)\)', item)
                    appendix.extend([f"[{text}]({url})" for text, url in links])
    
    with open(output_file, 'w', encoding='utf-8') as out:
        for category, entries in result.items():
            if entries:
                out.write(f"## {category}\n\n")
                for i, entry in enumerate(entries, 1):
                    out.write(f"{i}、{entry}\n\n")
                out.write('\n')
        
        # 输出附录
        if appendix:
            out.write("## 附录\n")
            for i, item in enumerate(appendix, 1):
                out.write(f"{i}、{item}\n\n")
            out.write('\n')

if __name__ == '__main__':
    extract_entries('docs/ss2.md', 'output2.md')
