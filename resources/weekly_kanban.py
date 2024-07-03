import os
import sqlite3
from pyecharts.charts import Bar, Pie, Tab
from pyecharts import options as opts
from pyecharts.globals import ThemeType, JsCode, SymbolType
import jieba
from collections import Counter
import re
from pyecharts.components import Image
from wordcloud import WordCloud

db_path = os.path.join(os.path.dirname(__file__), 'python_weekly.db')

color_map = {
    "文章": "#FFCC80",
    "项目": "#66bfbf",
    "音视频": "#A7FFEB",
    "讨论": "#ffc0c2",
    "赠书": "#9FA8DA"
}

def query_data():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        query = """
        SELECT issue_no, article_count, project_count, audio_video_count, hot_topic_count, book_count
        FROM weekly_summary
        """
        cursor.execute(query)
        data = cursor.fetchall()
    return data

def prepare_data(data, start, end):
    issue_nos, articles, projects, audio_video, hot_topics, books = [], [], [], [], [], []
    for issue_no, article_count, project_count, audio_video_count, hot_topic_count, book_count in data[start:end]:
        issue_nos.append(issue_no)
        articles.append(article_count)
        projects.append(project_count)
        audio_video.append(audio_video_count)
        hot_topics.append(hot_topic_count)
        books.append(book_count)
    return issue_nos, articles, projects, audio_video, hot_topics, books

def create_bar_chart(issue_nos, articles, projects, audio_video, hot_topics, books, color_map):
    bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.ESSOS))
    bar.add_xaxis(issue_nos)
    categories = ['文章', '项目', '音视频', '讨论', '赠书']
    for category, values in zip(categories, [articles, projects, audio_video, hot_topics, books]):
        color = color_map.get(category, "#000000")
        bar.add_yaxis(
            category,
            values,
            stack="总量",
            itemstyle_opts=opts.ItemStyleOpts(color=color),
            label_opts=opts.LabelOpts(is_show=True, formatter=JsCode(
                "function(params) { return params.value > 0 ? params.value : ''; }"
            ))
        )
    bar.set_global_opts(
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=0)),
        yaxis_opts=opts.AxisOpts(type_="value"),
        toolbox_opts=opts.ToolboxOpts(is_show=False)
    )
    return bar

def create_pie_chart(articles, projects, audio_video, hot_topics, books, color_map):
    pie = Pie(init_opts=opts.InitOpts(theme=ThemeType.ESSOS))
    categories = ['文章', '项目', '音视频', '讨论', '赠书']
    total_counts = [sum(articles), sum(projects), sum(audio_video), sum(hot_topics), sum(books)]
    category_colors = [color_map.get(category, "#000000") for category in categories]
    pie.add(
        "",
        [list(z) for z in zip(categories, total_counts)],
        radius="66%",
        label_opts=opts.LabelOpts(formatter="{c} ({d}%)"),
        itemstyle_opts={
            "color": JsCode("""
                function(params) {
                    var colorList = """ + str(category_colors) + """;
                    return colorList[params.dataIndex];
                }
            """)
        }
    )
    return pie

def create_echarts_tab(data, start, end, bar_tab, pie_tab, wc_tab, tab_name):
    issue_nos, articles, projects, audio_video, hot_topics, books = prepare_data(data, start, end)
    bar = create_bar_chart(issue_nos, articles, projects, audio_video, hot_topics, books, color_map)
    pie = create_pie_chart(articles, projects, audio_video, hot_topics, books, color_map)
    wc = create_wordcloud_chart(tab_name)

    bar_tab.add(bar, f"{tab_name}")
    pie_tab.add(pie, f"{tab_name}")
    wc_tab.add(wc, f"{tab_name}")


def create_wordcloud_chart(tab_name):
    img = Image()
    img.add(src=f"https://img.pythoncat.top/weekly_wordcloud_{tab_name[1]}.png", style_opts={
        "style": "max-width: 100%; height: auto; display: block; margin-left: auto; margin-right: auto;"
    }) 
    return img

def create_tabs_with_style(html_file):
    with open(html_file, 'r+', encoding='utf-8') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(content)

def render_html(bar_tab_html, pie_tab_html, wc_tab_html):
    bar_tab_html = bar_tab_html.rstrip('.html')
    pie_tab_html = pie_tab_html.rstrip('.html')
    wc_tab_html = wc_tab_html.rstrip('.html')
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Python潮流周刊 - Python爱好者必备的学习帮手</title>
        <script async src="https://pythoncat.zeabur.app/script.js" data-website-id="79b984fa-d00f-4e52-a8f2-ad8747cfd077"></script>
    </head>
    <body>
        <center><h1><a href="https://xiaobot.net/p/python_weekly">Python潮流周刊</a></h1></center>
        <center><h2>每期周刊内容统计</h2></center>
        <iframe src="{bar_tab_html}" width="100%" height="568px" frameborder="0"></iframe>
        <center><h2>每季周刊内容统计</h2></center>
        <iframe src="{pie_tab_html}" width="100%" height="588px" frameborder="0"></iframe>
        <center><h2>每季周刊的词云图</h2></center>
        <iframe src="{wc_tab_html}" width="100%" height="600px" frameborder="0"></iframe>
        <center><h3>&copy; <a href="https://twitter.com/chinesehuazhou">豌豆花下猫</a> | <a href="https://xiaobot.net/p/python_weekly">订阅周刊</a></h3></center>
    </body>
    </html>
    """
    with open('weekly_kanban.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    data = query_data()
    bar_tab = Tab()
    pie_tab = Tab()
    wc_tab = Tab()

    create_echarts_tab(data, 0, 30, bar_tab, pie_tab, wc_tab, '第1季')
    create_echarts_tab(data, 30, 60, bar_tab, pie_tab, wc_tab, '第2季')

    bar_tab_html = 'bar_tab.html'
    pie_tab_html = 'pie_tab.html'
    wc_tab_html = 'wc_tab.html'
    bar_tab.render(bar_tab_html)
    pie_tab.render(pie_tab_html)
    wc_tab.render(wc_tab_html)

    create_tabs_with_style(bar_tab_html)
    create_tabs_with_style(pie_tab_html)
    create_tabs_with_style(wc_tab_html)

    render_html(bar_tab_html, pie_tab_html, wc_tab_html)


main()