import os
import re
from dotenv.main import load_dotenv
import google.generativeai as genai

if not os.getenv('GEMINI_API_KEY'):
    load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"], transport="rest")
model = genai.GenerativeModel('gemini-pro')


def read_prompt(target_lang):
    filename = f"prompt/trans_to_{target_lang}.txt"
    with open(filename, 'r', encoding='utf-8') as file:
        prompt = file.read()
    return prompt


def get_gemini_translation(text, target_lang):
    prompt = read_prompt(target_lang) + text
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
                temperature=0.4,
            ),
        )
    except ValueError as e:
        print("Prompt was blocked. Feedback:", response.prompt_feedback)
        raise e

    return response.text


def parse_md(file_content):
    """
    解析markdown文件，返回正文内容的二级标题及其子条目
    :param file_content: md文件内容
    :return: 结构化的字典
    """
    pattern = r'(?=##\s)'
    sections = re.split(pattern, file_content)

    result = {}
    for section in sections:
        lines = section.strip().split('\n')
        key = lines[0]
        if not key.startswith("##") or "欢迎订阅" in key or "产品推荐" in key:
            continue
        sub_sections = re.split(r'(?=\n\d\W)', section)
        sub_sections = [s.strip() for s in sub_sections if s.strip() and s.strip() != key]
        result[key] = sub_sections
    return result

titles = {
    "🦄文章&教程": "🦄Articles & Tutorials",
    "🐿️项目&资源": "🐿️Projects & Resources",
    "🐢播客&视频": "🐢Podcasts & Videos"
}

def translate_and_write_to_file(input_file, output_file):
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

    with open(output_file, 'w', encoding="utf-8") as f:
        for key, value in translated_dict.items():
            f.write(titles[key] + '\n\n')
            for item in value:
                f.write(item + '\n\n')


translate_and_write_to_file('01-06--ying.md', 'output.md')

# translate_and_write_to_file('resources/01-06--ying.md', 'output.md')