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
    
    print("抓取 Google News (跨境电商)...")
    url_kuajing = "https://news.google.com/rss/search?q=%E8%B7%A8%E5%A2%83%E7%94%B5%E5%95%86&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    all_news["跨境电商 (综合资讯)"] = get_feed_data(url_kuajing, limit=8)
    
    print("抓取 Google News (品牌出海)...")
    url_chuhai = "https://news.google.com/rss/search?q=%E5%93%81%E7%89%8C%E5%87%BA%E6%B5%B7&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    all_news["品牌出海 (综合资讯)"] = get_feed_data(url_chuhai, limit=5)
    
    print("抓取 36氪 (出海/跨境相关)...")
    url_36kr = "https://36kr.com/feed"
    # 对于 36 氪，我们稍微多抓一点，因为要通过关键字过滤
    all_news["36氪 (创投/科技出海)"] = get_feed_data(url_36kr, limit=5, keyword="出海")
    
    return all_news

if __name__ == "__main__":
    res = fetch_daily_news()
    for k, v in res.items():
        print(f"--- {k} ---")
        for item in v:
            print(item['title'])
