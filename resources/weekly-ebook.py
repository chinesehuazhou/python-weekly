# 将当前目录的season1.md文件生成epub电子书，使用pandoc命令行工具
# 需要指定以下内容：
# 1、epub指定封面地址 ./img/cover.png
# 2、epub生成目录，所有的“##”内容都是一个章节标题，所有的“###”都是章节里的小标题
# 3、生成的epub电子书里的段落开头移除缩进
# 4、markdown里有引用本地图片文件，生成的电子书里也需要有图片

import os
import tempfile
import shutil
import zipfile
import pypandoc

def create_epub():
    cover = "./img/cover.png"
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(f"{temp_dir}/styles.css", "w") as f:
            f.write("p { text-indent: 0; }")
            f.write("p:empty { display: none; }")

        output_file = f"{temp_dir}/season1.epub"
        pypandoc.convert_file("season1.md", "epub", outputfile=output_file, 
            extra_args=['--toc', '--toc-depth=2', '--epub-chapter-level=2', f'--epub-cover-image={cover}', 
            '--from=markdown+smart', f'--css={temp_dir}/styles.css', '--metadata', 'toc-title=Contents'])

        with zipfile.ZipFile(output_file, 'r') as zip_ref:
            zip_ref.extractall(f"{temp_dir}/epub_content")

        toc_ncx_path = None
        for root, dirs, files in os.walk(f"{temp_dir}/epub_content"):
            if "toc.ncx" in files:
                toc_ncx_path = os.path.join(root, "toc.ncx")
                break

        if toc_ncx_path:
            # 移除多余的“Title Page”, “Cover”, “Table of Contents”
            with open(toc_ncx_path, 'r', encoding='utf-8') as file:
                toc_ncx_content = file.read()

            toc_ncx_content = toc_ncx_content.replace('<navPoint id="titlepage" playOrder="1">', '<!-- <navPoint id="titlepage" playOrder="1">')
            toc_ncx_content = toc_ncx_content.replace('</navPoint>', '</navPoint> -->', 1)

            # 移除空白页面
            toc_ncx_content = toc_ncx_content.replace('<navPoint id="blank" playOrder="2">', '<!-- <navPoint id="blank" playOrder="2">')
            toc_ncx_content = toc_ncx_content.replace('</navPoint>', '</navPoint> -->', 1)

            # 移除章节编号
            import re
            toc_ncx_content = re.sub(r'<text>[^<]*?(\d+\.\s)', '<text>', toc_ncx_content)

            with open(toc_ncx_path, 'w') as file:
                file.write(toc_ncx_content)

        # 将生成的epub复制到当前目录
        shutil.copy(output_file, "season1.epub")

if __name__ == "__main__":
    create_epub()
