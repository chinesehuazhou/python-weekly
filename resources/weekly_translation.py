import os
import textwrap
import markdown
from bs4 import BeautifulSoup, NavigableString
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
    prompt = read_prompt(target_lang)

    # Generate the text response using the model
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


def translate_html(html, target_lang):
    soup = BeautifulSoup(html, 'html.parser')

    for text_node in soup.find_all(string=True):
        if text_node.parent.name not in ['style', 'script']:
            translated_text = get_gemini_translation(text_node, target_lang)
            text_node.replace_with(NavigableString(translated_text))

    return str(soup)


def translate_and_write_to_file(input_file, output_file):
    with open(input_file, 'r', encoding="utf-8") as f:
        text = f.read()

    html = markdown.markdown(text)
    translated_html = translate_html(html, "en")
    translated_markdown = markdownify(translated_html)

    with open(output_file, 'w', encoding="utf-8") as f:
        f.write(translated_markdown)


translate_and_write_to_file('01-06--ying.md', 'output.md')