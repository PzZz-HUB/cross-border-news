import os
from scraper import fetch_daily_news
from web_builder import build_webpage

def main():
    print("开始执行每日资讯收集任务...")
    
    # 1. 抓取新闻并经过 AI 筛选
    news_data = fetch_daily_news()
    
    # 2. 生成静态网页
    if any(news_data.values()):
        build_webpage(news_data)
        print(f"抓取完成，共 {sum(len(v) for v in news_data.values())} 条新闻。")
    else:
        print("今日没有抓取到符合要求的新闻，无需生成网页。")

if __name__ == "__main__":
    main()
