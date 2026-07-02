from playwright.sync_api import sync_playwright
import time

def fetch_amazon_official(page):
    print("正在抓取 Amazon 官方新闻间...")
    news_list = []
    try:
        # Amazon Small Business News
        page.goto("https://www.aboutamazon.com/news/small-business", timeout=30000)
        # 等待主要内容加载
        page.wait_for_selector(".Promo-title", timeout=10000)
        
        # 查找带有 Promo-title 的链接
        elements = page.query_selector_all(".Promo-title a")
        for el in elements[:6]:
            title = el.inner_text().strip()
            link = el.get_attribute("href")
            if not link.startswith("http"):
                link = "https://www.aboutamazon.com" + link
            if title and link:
                news_list.append({
                    "title": title,
                    "link": link,
                    "summary": "Amazon 官方发布"
                })
    except Exception as e:
        print(f"抓取 Amazon 官方新闻失败: {e}")
    return news_list

def fetch_tiktok_official(page):
    print("正在抓取 TikTok 官方新闻间...")
    news_list = []
    try:
        # TikTok Global Newsroom
        page.goto("https://newsroom.tiktok.com/en-us/", timeout=30000)
        # 等待文章卡片加载
        page.wait_for_selector("article, .card", timeout=10000)
        
        # 提取链接和标题 (新闻间的常规 a 标签带有标题内容)
        elements = page.query_selector_all("a")
        for el in elements:
            title = el.inner_text().strip()
            link = el.get_attribute("href")
            # 过滤掉过短的无意义链接（如 Nav, Read More等）
            if len(title) > 20 and link and "/en-us/article/" in link:
                if not link.startswith("http"):
                    link = "https://newsroom.tiktok.com" + link
                    
                # 去重
                if link not in [n['link'] for n in news_list]:
                    news_list.append({
                        "title": title,
                        "link": link,
                        "summary": "TikTok 官方发布"
                    })
                
            if len(news_list) >= 6:
                break
    except Exception as e:
        print(f"抓取 TikTok 官方新闻失败: {e}")
    return news_list

def fetch_daily_news():
    print("启动浏览器直连官方数据源 (不再使用 AI)...")
    all_news = {}
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # 1. Amazon 官方
            amazon_news = fetch_amazon_official(page)
            if amazon_news:
                all_news["Amazon 官方"] = amazon_news
                
            # 2. TikTok 官方
            tiktok_news = fetch_tiktok_official(page)
            if tiktok_news:
                all_news["TikTok 官方"] = tiktok_news
                
            browser.close()
    except Exception as e:
        print(f"Playwright 抓取异常: {e}")
        
    return all_news

if __name__ == "__main__":
    res = fetch_daily_news()
    for platform, news_list in res.items():
        print(f"--- {platform} ---")
        for item in news_list:
            print(f"- {item['title']}")
