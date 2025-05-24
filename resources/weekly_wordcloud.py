"""
生成 Python 潮流周刊词云图

该脚本用于分析周刊内容，生成词云图，支持中英文混合统计。
主要功能：
1. 分离并统计中英文词频
2. 过滤停用词
3. 处理特殊词组（如版本号、专有名词等）
4. 生成词云图片
"""

import os
import re
import jieba
from collections import Counter
from wordcloud import WordCloud


def separate_chinese_and_english(text):
    """
    分离文本中的中文和英文
    
    Args:
        text (str): 输入文本
    
    Returns:
        tuple: (中文文本列表, 英文文本列表)
    """
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    english_pattern = re.compile(r'[A-Za-z]+')
    chinese_text = chinese_pattern.findall(text)
    english_text = english_pattern.findall(text)
    return chinese_text, english_text


def handle_special_cases(text):
    """
    处理特殊词组，如版本号、专有名词等
    
    Args:
        text (str): 输入文本
    
    Returns:
        list: 特殊词组列表
    """
    special_pattern = re.compile(r'(Python\s\d+\.\d+|GPT-\d+|f-string|Python潮流周刊|PEP-\d+)')
    special_text = special_pattern.findall(text)
    return special_text


def filter_stopwords(words, stopwords):
    """
    过滤停用词
    
    Args:
        words (list): 词列表
        stopwords (set): 停用词集合
    
    Returns:
        list: 过滤后的词列表
    """
    return [word for word in words if word not in stopwords]


def read_markdown_and_count_words(markdown_file_path):
    """
    读取 Markdown 文件并统计词频
    
    Args:
        markdown_file_path (str): Markdown 文件路径
    
    Returns:
        list: 词频统计结果，格式为 [(词, 频次), ...]
    """
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
    """
    创建词云图片
    
    Args:
        file_path (str): Markdown 文件路径
        season_no (int): 季度编号
    """
    # 确保输出目录存在
    output_dir = 'resources/img'
    os.makedirs(output_dir, exist_ok=True)
    
    img_name = f'{output_dir}/weekly_wordcloud_{season_no}.png'
    if os.path.exists(img_name):
        print(f'{img_name} already exists, skip creating wordcloud.')
        return

    words = read_markdown_and_count_words(file_path)
    word_freq = {word: freq for word, freq in words if freq > 5}
    
    # 使用系统字体
    font_path = '/System/Library/Fonts/Hiragino Sans GB.ttc'  # macOS 系统自带中文字体
    
    wc = WordCloud(
        font_path=font_path,
        background_color='white',
        width=800,
        height=520,
        max_font_size=120,
        max_words=180
    )
    wc.generate_from_frequencies(word_freq)
    wc.to_file(img_name)


def main():
    """主函数：生成第三季度的词云图"""
    create_wordcloud_img('./docs/season_3.md', 3)


if __name__ == "__main__":
    main()