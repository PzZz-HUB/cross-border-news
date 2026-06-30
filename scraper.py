import requests
import feedparser
from bs4 import BeautifulSoup

def get_feed_data(url, limit=5, keywords=None):
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
            
            # 如果提供了关键词，则严格过滤
            if keywords:
                if not any(k in title for k in keywords):
                    continue
                    
            if title and link not in [n['link'] for n in news_list]:
                news_list.append({"title": title, "link": link})
                if len(news_list) >= limit:
                    break
    except Exception as e:
        print(f"获取 RSS 失败: {url}, 错误: {e}")
        
    return news_list

def fetch_cifnews():
    url = "https://www.cifnews.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    news_list = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            if '/article/' in a['href']:
                title = a.text.strip()
                link = "https://www.cifnews.com" + a['href'] if a['href'].startswith('/') else a['href']
                # 过滤掉无效或太短的标题
                if title and len(title) > 6 and link not in [n['link'] for n in news_list]:
                    news_list.append({"title": title, "link": link})
                if len(news_list) >= 8:
                    break
    except Exception as e:
        print(f"获取雨果网失败: {e}")
    return news_list

def fetch_daily_news():
    all_news = {}
    
    print("抓取 雨果跨境 (专业跨境电商资讯)...")
    all_news["雨果跨境 (最新干货)"] = fetch_cifnews()
    
    print("抓取 36氪 (出海精选)...")
    url_36kr = "https://36kr.com/feed"
    keywords = ["出海", "跨境", "亚马逊", "TikTok", "Shopee", "独立站", "速卖通", "海外"]
    all_news["36氪 (商业出海)"] = get_feed_data(url_36kr, limit=6, keywords=keywords)
    
    return all_news

if __name__ == "__main__":
    res = fetch_daily_news()
    for k, v in res.items():
        print(f"--- {k} ---")
        for item in v:
            print(item['title'])
