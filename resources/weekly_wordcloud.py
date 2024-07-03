import os
import re
import jieba
from collections import Counter
from wordcloud import WordCloud


def separate_chinese_and_english(text):
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    english_pattern = re.compile(r'[A-Za-z]+')
    chinese_text = chinese_pattern.findall(text)
    english_text = english_pattern.findall(text)
    return chinese_text, english_text

def handle_special_cases(text):
    special_pattern = re.compile(r'(Python\s\d+\.\d+|GPT-\d+|f-string|Python潮流周刊|PEP-\d+)')
    special_text = special_pattern.findall(text)
    return special_text

def filter_stopwords(words, stopwords):
    return [word for word in words if word not in stopwords]

def read_markdown_and_count_words(markdown_file_path):
    with open(markdown_file_path, 'r', encoding='utf-8') as file:
        markdown_text = file.read()

    markdown_text = re.sub(r'\[.*?\]\(.*?\)', '', markdown_text)
    markdown_text = re.sub(r'-{2,}', '', markdown_text)
    chinese_text, english_text = separate_chinese_and_english(markdown_text)

    chinese_words = []
    for text in chinese_text:
        chinese_words.extend(jieba.cut(text, cut_all=False))
    english_words = []
    for word in english_text:
        if len(word) > 1:
            english_words.append(word)

    stop_words_path = os.path.join(os.path.dirname(__file__), 'stop_words.txt')
    with open(stop_words_path, encoding='utf-8') as f:
        stop_words = set(line.strip() for line in f.readlines())

    filtered_chinese_words = filter_stopwords(chinese_words, stop_words)
    filtered_english_words = filter_stopwords(english_words, stop_words)
    special_words = handle_special_cases(markdown_text)
    all_words = filtered_chinese_words + filtered_english_words + special_words
    word_freq = Counter(all_words)
    return list(word_freq.items())

def create_wordcloud_img(file_path, season_no):
    img_name = f'resources/img/weekly_wordcloud_{season_no}.png'
    if os.path.exists(img_name):
        print(f'{img_name} already exists, skip creating wordcloud.')
        return

    words = read_markdown_and_count_words(file_path)
    word_freq = {word: freq for word, freq in words if freq > 5}
    
    wc = WordCloud(font_path='msyh.ttc', background_color='white', width=800, height=520, max_font_size=120, max_words=180)
    wc.generate_from_frequencies(word_freq)
    wc.to_file(img_name)

def main():
    create_wordcloud_img('./docs/2023-12-11-sweekly.md', 1)

main()