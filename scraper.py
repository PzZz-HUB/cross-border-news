import requests
from bs4 import BeautifulSoup
import re
from deep_translator import GoogleTranslator

def fetch_amazon_official():
    print("正在抓取 Amazon 全球开店 (官方中文) 新闻间...")
    news_list = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        # 亚马逊全球开店官方新闻
        r = requests.get("https://gs.amazon.cn/news", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        for a in soup.find_all('a'):
            title = a.text.strip()
            href = a.get('href', '')
            
            # 过滤有效的亚马逊新闻链接
            if '/news/news-' in href and len(title) > 6:
                link = href if href.startswith('http') else "https://gs.amazon.cn" + href
                # 去重
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
    print("正在抓取 TikTok 官方新闻间并进行自动翻译...")
    news_list = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get("https://newsroom.tiktok.com/en-us/", headers=headers, timeout=15)
        
        # TikTok 新闻间的数据通常通过 Next.js 的 SSR 嵌入在脚本或 JSON 数据中
        # 使用正则表达式提取内嵌的标题和链接
        matches = re.findall(r'"title":"([^"]+)","url":"([^"]+)"', r.text)
        
        translator = GoogleTranslator(source='auto', target='zh-CN')
        
        seen_links = set()
        for title, url in matches:
            if '/en-us/article/' in url and len(title) > 10:
                link = url if url.startswith('http') else "https://newsroom.tiktok.com" + url
                if link not in seen_links:
                    seen_links.add(link)
                    
                    try:
                        translated_title = translator.translate(title)
                    except Exception:
                        translated_title = title # 翻译失败降级为原英文
                        
                    news_list.append({
                        "title": translated_title,
                        "link": link,
                        "summary": "TikTok 官方发布 (机器翻译)"
                    })
                    
            if len(news_list) >= 8:
                break
    except Exception as e:
        print(f"抓取 TikTok 官方新闻失败: {e}")
    return news_list

def fetch_daily_news():
    print("启动直连官方数据源 (直接抓取官方中文内容/自动翻译)...")
    all_news = {}
    
    # 1. Amazon 官方 (全球开店中文网)
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
