import requests
import feedparser
from bs4 import BeautifulSoup
from ai_judge import filter_news_with_ai

# 通用屏蔽词（黑名单），如果标题包含这些词，直接丢弃
EXCLUDE_KEYWORDS = [
    "招商", "报名", "峰会", "直播", "课程", 
    "培训", "咨询", "服务商", "开店顾问", "会员", 
    "活动", "大会", "交流群", "广告"
]

def is_valid_news(title, include_keywords=None):
    # 1. 检查黑名单屏蔽词
    for bad_word in EXCLUDE_KEYWORDS:
        if bad_word in title:
            return False
            
    # 2. 如果有白名单强制关键词，检查是否包含
    if include_keywords:
        if not any(k in title for k in include_keywords):
            return False
            
    return True

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
            
            if not is_valid_news(title, include_keywords=keywords):
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
                
                # 过滤掉过短的标题和黑名单内容
                if title and len(title) > 6 and is_valid_news(title):
                    if link not in [n['link'] for n in news_list]:
                        news_list.append({"title": title, "link": link})
                        
                if len(news_list) >= 8:
                    break
    except Exception as e:
        print(f"获取雨果网失败: {e}")
    return news_list

def fetch_daily_news():
    all_news = {}
    
    print("抓取 雨果跨境 (专业跨境电商资讯)...")
    cifnews_raw = fetch_cifnews()
    all_news["雨果跨境 (最新干货)"] = filter_news_with_ai(cifnews_raw)
    
    print("抓取 36氪 (出海精选)...")
    url_36kr = "https://36kr.com/feed"
    # 白名单：必须包含这些词才抓取
    keywords = ["出海", "跨境", "亚马逊", "TikTok", "Shopee", "独立站", "速卖通", "海外"]
    kr_raw = get_feed_data(url_36kr, limit=6, keywords=keywords)
    all_news["36氪 (商业出海)"] = filter_news_with_ai(kr_raw)
    
    return all_news

if __name__ == "__main__":
    res = fetch_daily_news()
    for k, v in res.items():
        print(f"--- {k} ---")
        for item in v:
            print(item['title'])
