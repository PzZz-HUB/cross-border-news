import requests
from bs4 import BeautifulSoup
import re

def fetch_amazon_official():
    print("正在抓取 Amazon 官方新闻间...")
    news_list = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        r = requests.get("https://www.aboutamazon.com/news/small-business", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # 查找包含 Promo-title 或类的链接
        for a in soup.find_all('a'):
            title = a.text.strip()
            href = a.get('href', '')
            
            # 过滤短标题，确保是新闻链接
            if '/news/small-business/' in href and len(title) > 10:
                link = href if href.startswith('http') else "https://www.aboutamazon.com" + href
                if link not in [n['link'] for n in news_list]:
                    news_list.append({
                        "title": title,
                        "link": link,
                        "summary": "Amazon 官方发布"
                    })
            if len(news_list) >= 8:
                break
    except Exception as e:
        print(f"抓取 Amazon 官方新闻失败: {e}")
    return news_list

def fetch_tiktok_official():
    print("正在抓取 TikTok 官方新闻间...")
    news_list = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get("https://newsroom.tiktok.com/en-us/", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        for a in soup.find_all('a'):
            title = a.text.strip()
            href = a.get('href', '')
            
            if '/en-us/article/' in href and len(title) > 15:
                link = href if href.startswith('http') else "https://newsroom.tiktok.com" + href
                if link not in [n['link'] for n in news_list]:
                    news_list.append({
                        "title": title,
                        "link": link,
                        "summary": "TikTok 官方发布"
                    })
            if len(news_list) >= 8:
                break
    except Exception as e:
        print(f"抓取 TikTok 官方新闻失败: {e}")
    return news_list

def fetch_daily_news():
    print("启动直连官方数据源 (极致轻量级爬虫，无需 AI 与浏览器引擎)...")
    all_news = {}
    
    # 1. Amazon 官方
    amazon_news = fetch_amazon_official()
    if amazon_news:
        all_news["Amazon 官方"] = amazon_news
        
    # 2. TikTok 官方
    tiktok_news = fetch_tiktok_official()
    if tiktok_news:
        all_news["TikTok 官方"] = tiktok_news
        
    return all_news

if __name__ == "__main__":
    res = fetch_daily_news()
    for platform, news_list in res.items():
        print(f"--- {platform} ---")
        for item in news_list:
            print(f"- {item['title']}")
