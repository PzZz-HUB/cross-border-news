import os
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
import google.generativeai as genai
from scraper import fetch_daily_news
from web_builder import build_webpage

def ai_is_relevant(title):
    # 1. 极速本地黑名单过滤
    blacklist = ["党建", "周年", "庆典", "合唱", "歌曲", "红船谣", "党委", "纪委", "党支部", "党课", "晚会", "歌咏", "比赛", "走访慰问", "离退休"]
    for word in blacklist:
        if word in title:
            reason = f"[黑名单拦截] 触发关键词: {word}"
            print(f" {reason} -> {title}")
            return False, reason

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(f" [警告] 未配置 GEMINI_API_KEY，默认通过此新闻: {title}")
        return True, "API Key Missing, Default Pass"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
你是一个无情的二极管过滤器。以下是一条电商平台或政府发布的官方新闻标题：
"{title}"
请判断这条新闻是否与【跨境电商卖家】有关（比如关税、平台政策、运营更新、物流变动）。
如果它纯粹是企业内部事件、国家庆典或娱乐（比如高管变动、慈善捐款、颁奖典礼、社区服务、晚会、党建、歌曲、合唱等）请判断为无关。
只需要回答 True 或者 False，不要回答任何其他多余的字。
"""
        response = model.generate_content(prompt)
        text = response.text.strip().lower()
        if text.startswith('false') or 'false' in text:
            return False, "[AI 智能拦截] 判定为无关公关稿"
        return True, "AI Passed"
    except Exception as e:
        print(f"AI 过滤请求失败，默认通过 ({title}): {e}")
        return True, f"AI Error: {e}"

def filter_with_ai(news_data):
    print("开始清洗去噪，被剔除的资讯将进入隔离审查区...")
    kept_data = {}
    quarantined_data = []
    
    for source, articles in news_data.items():
        kept_articles = []
        for a in articles:
            is_rel, reason = ai_is_relevant(a['title'])
            if is_rel:
                kept_articles.append(a)
            else:
                a['reject_reason'] = reason
                a['source'] = source
                quarantined_data.append(a)
        if kept_articles:
            kept_data[source] = kept_articles
            
    print(f"去噪完成：保留 {sum(len(v) for v in kept_data.values())} 条，隔离 {len(quarantined_data)} 条。")
    return kept_data, quarantined_data

def main():
    print("开始执行每日资讯收集任务...")
    
    # 1. 抓取新闻 (纯官方，仅限当天)
    news_data, source_statuses = fetch_daily_news()
    
    # 2. 经过多层过滤 (黑名单 + AI)
    kept_news = {}
    quarantined_news = []
    if news_data:
        kept_news, quarantined_news = filter_with_ai(news_data)
    
    # 3. 生成包含大盘和隔离区的静态网页
    build_webpage(kept_news, quarantined_news, source_statuses)
    print("今日任务全部执行完毕！")

if __name__ == "__main__":
    main()
