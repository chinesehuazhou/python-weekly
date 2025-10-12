"""
Python 潮流周刊数据可视化看板生成器

该脚本用于生成 Python 潮流周刊的数据统计看板，包括：
1. 每期周刊的内容分类统计（柱状图）
2. 每季度的内容分布统计（饼图）
3. 每季度的关键词词云图

使用 pyecharts 生成交互式图表，支持按季度查看统计数据。
数据来源：SQLite 数据库（python_weekly.db）
"""

import os
import sqlite3
from pyecharts.charts import Bar, Pie, Tab
from pyecharts import options as opts
from pyecharts.globals import ThemeType, JsCode
import re
from pyecharts.components import Image

# 数据库文件路径
db_path = os.path.join(os.path.dirname(__file__), 'python_weekly.db')

# 定义各类内容的颜色映射
color_map = {
    "文章": "#FFCC80",  # 橙色
    "项目": "#66bfbf",  # 青色
    "音视频": "#A7FFEB",  # 薄荷绿
    "讨论": "#ffc0c2",  # 粉色
    "赠书": "#9FA8DA"   # 淡紫色
}

def query_data():
    """
    从数据库查询周刊内容统计数据
    
    Returns:
        list: 包含期号和各类内容数量的元组列表
    """
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
    """
    将数据库查询结果转换为图表所需的数据格式
    
    Args:
        data (list): 原始数据列表
        start (int): 起始索引
        end (int): 结束索引
    
    Returns:
        tuple: 包含期号和各类内容数量的列表元组
    """
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
    """
    创建堆叠柱状图，展示每期周刊的内容分布
    
    Args:
        issue_nos (list): 期号列表
        articles (list): 文章数量列表
        projects (list): 项目数量列表
        audio_video (list): 音视频数量列表
        hot_topics (list): 讨论话题数量列表
        books (list): 赠书数量列表
        color_map (dict): 内容类型与颜色的映射
    
    Returns:
        Bar: pyecharts Bar 图表对象
    """
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
    """
    创建饼图，展示一个季度内容的整体分布
    
    Args:
        articles (list): 文章数量列表
        projects (list): 项目数量列表
        audio_video (list): 音视频数量列表
        hot_topics (list): 讨论话题数量列表
        books (list): 赠书数量列表
        color_map (dict): 内容类型与颜色的映射
    
    Returns:
        Pie: pyecharts Pie 图表对象
    """
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
    """
    创建一个季度的所有图表并添加到对应的标签页
    
    Args:
        data (list): 原始数据列表
        start (int): 起始索引
        end (int): 结束索引
        bar_tab (Tab): 柱状图标签页对象
        pie_tab (Tab): 饼图标签页对象
        wc_tab (Tab): 词云图标签页对象
        tab_name (str): 标签页名称（如"第1季"）
    """
    issue_nos, articles, projects, audio_video, hot_topics, books = prepare_data(data, start, end)
    bar = create_bar_chart(issue_nos, articles, projects, audio_video, hot_topics, books, color_map)
    pie = create_pie_chart(articles, projects, audio_video, hot_topics, books, color_map)
    wc = create_wordcloud_chart(tab_name)

    bar_tab.add(bar, f"{tab_name}")
    pie_tab.add(pie, f"{tab_name}")
    wc_tab.add(wc, f"{tab_name}")

def create_wordcloud_chart(tab_name):
    """
    创建词云图组件，展示一个季度的关键词分布
    
    Args:
        tab_name (str): 标签页名称，用于确定加载哪个词云图
    
    Returns:
        Image: pyecharts Image 组件对象
    """
    img = Image()
    img.add(src=f"https://img.pythoncat.top/weekly_wordcloud_{tab_name[1]}.png", style_opts={
        "style": "max-width: 100%; height: auto; display: block; margin-left: auto; margin-right: auto;"
    }) 
    return img

def create_tabs_with_style(html_file):
    """
    为生成的 HTML 文件添加自定义样式
    
    Args:
        html_file (str): HTML 文件路径
    """
    with open(html_file, 'r+', encoding='utf-8') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(content)

def render_html(bar_tab_html, pie_tab_html, wc_tab_html):
    """
    生成最终的 HTML 页面，整合所有图表
    
    Args:
        bar_tab_html (str): 柱状图 HTML 文件路径
        pie_tab_html (str): 饼图 HTML 文件路径
        wc_tab_html (str): 词云图 HTML 文件路径
    """
    bar_tab_html = bar_tab_html.rstrip('.html')
    pie_tab_html = pie_tab_html.rstrip('.html')
    wc_tab_html = wc_tab_html.rstrip('.html')
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Python潮流周刊 - Python爱好者必备的学习帮手</title>
        <script async src="https://cloud.umami.is/script.js" data-website-id="2cbc7625-5017-43f4-aed7-6e333acc65de"></script>
        <script>
            function resizeIframe(obj) {{
                obj.style.height = obj.contentWindow.document.documentElement.scrollHeight + 'px';
            }}
        </script>
    </head>
    <body>
        <center><h1><a href="https://xiaobot.net/p/python_weekly">Python潮流周刊</a></h1></center>
        <center><h2>每期周刊内容统计</h2></center>
        <iframe src="{bar_tab_html}" width="100%" height="568px" frameborder="0"></iframe>
        <center><h2>每季周刊内容统计</h2></center>
        <iframe src="{pie_tab_html}" width="100%" height="588px" frameborder="0"></iframe>
        <center><h2>每季周刊的词云图</h2></center>
        <iframe src="{wc_tab_html}" width="100%" frameborder="0" onload="resizeIframe(this)"></iframe>
        <center><h3>&copy; <a href="https://twitter.com/chinesehuazhou">豌豆花下猫</a> | <a href="https://xiaobot.net/p/python_weekly">订阅周刊</a></h3></center>
    </body>
    </html>
    """
    with open('weekly_kanban.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    """
    主函数：执行数据查询、图表生成和HTML渲染的完整流程
    """
    # 查询数据库获取统计数据
    data = query_data()
    
    # 创建三个标签页容器
    bar_tab = Tab()
    pie_tab = Tab()
    wc_tab = Tab()

    # 生成第一季度的图表（1-30期）
    create_echarts_tab(data, 0, 30, bar_tab, pie_tab, wc_tab, '第1季')
    # 生成第二季度的图表（31-60期）
    create_echarts_tab(data, 30, 60, bar_tab, pie_tab, wc_tab, '第2季')
    # 生成第三季度的图表（61-90期）
    create_echarts_tab(data, 60, 90, bar_tab, pie_tab, wc_tab, '第3季')
        # 生成第三季度的图表（91-120期）
    create_echarts_tab(data, 90, 120, bar_tab, pie_tab, wc_tab, '第4季')

    # 定义输出文件名
    bar_tab_html = 'bar_tab.html'
    pie_tab_html = 'pie_tab.html'
    wc_tab_html = 'wc_tab.html'
    
    # 渲染各个图表
    bar_tab.render(bar_tab_html)
    pie_tab.render(pie_tab_html)
    wc_tab.render(wc_tab_html)

    # 添加自定义样式
    create_tabs_with_style(bar_tab_html)
    create_tabs_with_style(pie_tab_html)
    create_tabs_with_style(wc_tab_html)

    # 生成最终的HTML页面
    render_html(bar_tab_html, pie_tab_html, wc_tab_html)


if __name__ == "__main__":
    main()