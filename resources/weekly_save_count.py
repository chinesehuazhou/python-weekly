import sqlite3
import os
import re

db_path = os.path.join(os.path.dirname(__file__), 'python_weekly.db')

def create_table():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_summary (
            issue_no INTEGER PRIMARY KEY,
            date TEXT,
            article_count INTEGER,
            project_count INTEGER,
            audio_video_count INTEGER,
            hot_topic_count INTEGER,
            book_count INTEGER
        )
        ''')


def parse_markdown():
    readme_path = 'README.md'
    with open(readme_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    pattern = r'(?<=往期列表)(.*?)(?=\n## )'
    section = re.search(pattern, content, re.DOTALL)
    if not section:
        return []
    
    entries = []
    lines = section.group(0).splitlines()
    for i in range(len(lines)):
        issue_date_match = re.match(r'- 第 (\d+) 期：.*?\[(.*?)\]\(.*?(\d{4}-\d{2}-\d{2})-weekly.md\)', lines[i])
        if issue_date_match:
            issue_no = int(issue_date_match.group(1))
            date = issue_date_match.group(3)
            
            # 从下一行开始匹配文章数、开源项目数、音视频数、热门话题数、赠书数
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                article_count = int(re.search(r'(\d+) 篇', next_line).group(1)) if re.search(r'(\d+) 篇', next_line) else 0
                project_count = int(re.search(r'(\d+) 个开源', next_line).group(1)) if re.search(r'(\d+) 个开源', next_line) else 0
                
                audio_video_match = re.search(r'(\d+) 则音|(\d+) 则视|(\d+) 则播', next_line)
                if audio_video_match:
                    audio_video_count = int(audio_video_match.group(1) or audio_video_match.group(2) or audio_video_match.group(3) or 0)
                else:
                    audio_video_count = 0
                
                hot_topic_count = int(re.search(r'(\d+) 个热门', next_line).group(1)) if re.search(r'(\d+) 个热门', next_line) else 0
                book_count = int(re.search(r'赠书 (\d+) 本', next_line).group(1)) if re.search(r'赠书 (\d+) 本', next_line) else 0
                
                entries.append({
                    'issue_no': issue_no,
                    'date': date,
                    'article_count': article_count,
                    'project_count': project_count,
                    'audio_video_count': audio_video_count,
                    'hot_topic_count': hot_topic_count,
                    'book_count': book_count
                })
    return entries

def insert_into_database(entries):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        for entry in entries:
            cursor.execute('SELECT issue_no FROM weekly_summary WHERE issue_no = ?', (entry['issue_no'],))
            if cursor.fetchone() is None:
                cursor.execute('''
                INSERT INTO weekly_summary (issue_no, date, article_count, project_count, audio_video_count, hot_topic_count, book_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry['issue_no'], 
                    entry['date'], 
                    entry.get('article_count', 0),
                    entry.get('project_count', 0), 
                    entry.get('audio_video_count', 0), 
                    entry.get('hot_topic_count', 0),  
                    entry.get('book_count', 0) 
                ))

def print_all_data():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM weekly_summary')
        rows = cursor.fetchall()
        for row in rows:
            print(f"Issue Number: {row[0]}, Date: {row[1]}, Articles: {row[2]}, Projects: {row[3]}, Audio/Video: {row[4]}, Hot Topics: {row[5]}, Books: {row[6]}")


def main():
    create_table()
    entries = parse_markdown()
    if entries:
        insert_into_database(entries)
    print_all_data()

main()

