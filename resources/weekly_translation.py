import functools
import os
import re
import time
from pathlib import Path
from dotenv.main import load_dotenv
import google.generativeai as genai

if not os.getenv('GEMINI_API_KEY'):
    load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"], transport="rest")
model = genai.GenerativeModel('gemini-pro')

titles = {
    "🦄文章&教程": "🦄Articles & Tutorials",
    "🐿️项目&资源": "🐿️Projects & Resources",
    "🐢播客&视频": "🐢Podcasts & Videos",
    "🥂讨论&问题": "🥂Discussion & Questions"
}

def read_prompt(target_lang):
    filename = f"resources/prompt/trans_to_{target_lang}.txt"
    with open(filename, 'r', encoding='utf-8') as file:
        prompt = file.read()
    return prompt


def retry(max_retries, delay):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"An error occurred: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
            raise Exception("Exceeded maximum retries")
        return wrapper
    return decorator


@retry(5, 3)
def get_gemini_translation(text, target_lang):
    print(f"Translating text with length of {len(text)}")
    prompt = read_prompt(target_lang) + '{{' + text + '}}'
    try:
        response = model.generate_content(
            prompt,
            safety_settings={
                "HARM_CATEGORY_HARASSMENT": "block_none",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "block_none",
                "HARM_CATEGORY_HATE_SPEECH": "block_none",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "block_none",
            },
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                temperature=0.2,
            ),
        )
        return response.text
    except ValueError as e:
        print("Failed to get gemini translation: ", response.prompt_feedback)
        raise e


def parse_md(file_content):
    """
    解析markdown文件，返回正文内容的二级标题及其子条目
    :param file_content: md文件内容
    :return: 结构化的字典
    """
    print(f"Parsing file content with length of {len(file_content)}")
    pattern = r'(?=##\s)'
    sections = re.split(pattern, file_content)
    result = {}
    for section in sections:
        lines = section.strip().split('\n')
        key = lines[0].strip("## ")
        if key not in titles:
            continue
        sub_sections = re.split(r'(?=\n\d\W)', section)
        sub_sections = [part for part in sub_sections if re.match(r'\n\d\W', part)]
        result[key] = sub_sections
    return result


def extract_weekly_no(file_path):
    """默认文件第二行为标题，解析期数"""
    print(f"Extracting weekly number from {file_path}")
    with open(file_path, 'r', encoding="utf-8") as f:
        lines = f.readlines()
        match = re.search(r'#(\d+)', lines[1])
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid weekly no format in the second line.")


def get_translated_dict(input_file):
    """
    解析正文内容，拆分进行翻译，返回翻译后的结构化信息
    """
    print(f"Translating file {input_file}")
    with open(input_file, 'r', encoding="utf-8") as f:
        text = f.read()
        content_dict = parse_md(text)
        translated_dict = {}
        for key, value in content_dict.items():
            translated_value = []
            for item in value:
                translated_item = get_gemini_translation(item, "en")
                translated_value.append(translated_item)
            translated_dict[key] = translated_value
        return translated_dict


def get_template_content(weekly_no, pub_date, translated_dict):
    """
    读取模板文件，填充元数据和翻译的正文，删除模板中多余的内容
    """
    print(f"Filling the template for weekly {weekly_no}")
    template_path = "resources/weekly_template_en.md"
    with open(template_path, 'r', encoding="utf-8") as f:
        template_content = f.read()
        template_content = template_content.format(weekly_no=weekly_no, pub_date=pub_date)
        extra_titles = [titles[key] for key in titles if key not in translated_dict]
        for extra_title in extra_titles:
            template_content = template_content.replace(f"## {extra_title}\n\n", "")
        for key, value in translated_dict.items():
            en_title = titles[key]
            template_content = template_content.replace(en_title, en_title + "\n\n" + "\n\n".join(value))
        return template_content


def translate_and_write_to_file(input_file, output_file, pub_date):
    translated_dict = get_translated_dict(input_file)
    weekly_no = extract_weekly_no(input_file)
    template_content = get_template_content(weekly_no, pub_date, translated_dict)
    print(f"Writing translated file to {output_file}")
    with open(output_file, 'w', encoding="utf-8") as f:
        f.write(template_content)

def translate_old_post():
    docs_dir = Path('docs')
    en_dir = docs_dir / 'en'
    for filepath in docs_dir.glob('2023-*-weekly.md'):
        en_filepath = en_dir / filepath.name
        if not en_filepath.exists():
            pub_date = filepath.name[:10]
            translate_and_write_to_file(filepath, en_filepath, pub_date)


def translate_cur_post(pub_date):
    filepath = Path(f"resources/{pub_date}-weekly.md")
    en_dir = Path("docs/en")
    en_filepath = en_dir / filepath.name
    if not en_filepath.exists():
        pub_date = filepath.name[:10]
        translate_and_write_to_file(filepath, en_filepath, pub_date)


def main():
    translate_cur_post("2024-01-13")
    # translate_old_post()


main()




# TODO：子标题和图片还有问题，偶现：缺文字链接