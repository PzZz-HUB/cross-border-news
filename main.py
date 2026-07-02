import os
import google.generativeai as genai
from scraper import fetch_daily_news
from web_builder import build_webpage

def ai_is_relevant(title):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return True # 如果没有 API Key，就不进行过滤，默认全量通过
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
你是一个无情的二极管过滤器。以下是一条电商平台或政府发布的官方新闻标题：
"{title}"
请判断这条新闻是否与【跨境电商卖家】有关（比如关税、平台政策、运营更新、物流变动）。
如果它纯粹是企业内部事件（比如高管变动、慈善捐款、颁奖典礼、社区服务）请判断为无关。
只需要回答 True 或者 False，不要回答任何其他多余的字。
"""
        response = model.generate_content(prompt)
        text = response.text.strip().lower()
        if 'false' in text and 'true' not in text:
            return False
        return True
    except Exception as e:
        print(f"AI 过滤请求失败，默认通过: {e}")
        return True

def filter_with_ai(news_data):
    print("开始 AI 智能去噪（仅剔除无关资讯）...")
    filtered_data = {}
    total_removed = 0
    for source, articles in news_data.items():
        kept_articles = []
        for a in articles:
            if ai_is_relevant(a['title']):
                kept_articles.append(a)
            else:
                total_removed += 1
                print(f" [AI 剔除] {a['title']}")
        if kept_articles:
            filtered_data[source] = kept_articles
    
    print(f"AI 去噪完成，共剔除 {total_removed} 条无关公关稿。")
    return filtered_data

def main():
    print("开始执行每日资讯收集任务...")
    
    # 1. 抓取新闻 (纯官方，仅限当天)
    news_data = fetch_daily_news()
    
    # 2. 经过 AI 轻量级判定过滤 (不翻译，不总结)
    if any(news_data.values()):
        news_data = filter_with_ai(news_data)
    
    # 3. 生成静态网页
    if any(news_data.values()):
        build_webpage(news_data)
        print(f"抓取完成，最终保留 {sum(len(v) for v in news_data.values())} 条高价值新闻。")
    else:
        print("今日没有抓取到符合要求的新闻，无需生成网页。")

if __name__ == "__main__":
    main()
