import requests
import feedparser
from datetime import datetime, timedelta

def get_feed_data(url, limit=5, keyword=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    news_list = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        feed = feedparser.parse(response.text)
        
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            
            if keyword and keyword not in title:
                continue
                
            if title and link not in [n['link'] for n in news_list]:
                news_list.append({"title": title, "link": link})
                if len(news_list) >= limit:
                    break
    except Exception as e:
        print(f"获取 RSS 失败: {url}, 错误: {e}")
        
    return news_list

def fetch_daily_news():
    all_news = {}
    
    # 因为 Google News 在国内存在重定向被拦截的问题，所以我们替换为国内可以直接点击的原生直链 RSS 源
    
    print("抓取 36氪...")
    url_36kr = "https://36kr.com/feed"
    # 获取 36氪 最新商业与科技动态
    all_news["36氪 (商业/创投动态)"] = get_feed_data(url_36kr, limit=8)
    
    print("抓取 钛媒体...")
    url_tmt = "https://www.tmtpost.com/rss.xml"
    # 获取钛媒体前瞻资讯
    all_news["钛媒体 (前沿商业)"] = get_feed_data(url_tmt, limit=5)
    
    return all_news

if __name__ == "__main__":
    res = fetch_daily_news()
    for k, v in res.items():
        print(f"--- {k} ---")
        for item in v:
            print(item['title'])
