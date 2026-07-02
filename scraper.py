import requests
from bs4 import BeautifulSoup
import re
import feedparser

def fetch_amazon_official():
    print("正在抓取 Amazon 官方新闻间...")
    news_list = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        r = requests.get("https://www.aboutamazon.com/news/small-business", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        for a in soup.find_all('a'):
            title = a.text.strip()
            href = a.get('href', '')
            
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
            
            if href.startswith('/') and len(href) > 20 and not href.startswith('/?') and len(title) > 10:
                if '/tag/' not in href and '/author/' not in href:
                    if title.startswith('News'):
                        title = title[4:].strip()
                    elif title.startswith('Product'):
                        title = title[7:].strip()
                        
                    link = "https://newsroom.tiktok.com" + href
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

def fetch_federal_register():
    print("正在抓取 Federal Register 官方 API...")
    news_list = []
    try:
        r = requests.get("https://www.federalregister.gov/api/v1/documents.json?conditions[type][]=NOTICE&per_page=8", timeout=15)
        data = r.json()
        for item in data.get('results', []):
            news_list.append({
                "title": item.get('title'),
                "link": item.get('html_url'),
                "summary": "Federal Register 官方通告"
            })
    except Exception as e:
        print(f"抓取 Federal Register 失败: {e}")
    return news_list

def fetch_shopify_changelog():
    print("正在抓取 Shopify Changelog...")
    news_list = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get("https://changelog.shopify.com/feed.xml", headers=headers, timeout=15)
        feed = feedparser.parse(r.text)
        for entry in feed.entries[:8]:
            news_list.append({
                "title": entry.title,
                "link": entry.link,
                "summary": "Shopify 官方发布"
            })
    except Exception as e:
        print(f"抓取 Shopify 失败: {e}")
    return news_list

def fetch_gov_uk():
    print("正在抓取 GOV.UK (英国政府) 通告...")
    news_list = []
    try:
        r = requests.get("https://www.gov.uk/search/news-and-communications.atom", timeout=15)
        feed = feedparser.parse(r.text)
        for entry in feed.entries[:8]:
            news_list.append({
                "title": entry.title,
                "link": entry.link,
                "summary": "GOV.UK 官方通告"
            })
    except Exception as e:
        print(f"抓取 GOV.UK 失败: {e}")
    return news_list

def fetch_google_news_rss(domain, source_name, lang="en-US", gl="US", ceid="US:en"):
    print(f"正在通过官方索引抓取 {source_name}...")
    news_list = []
    try:
        url = f"https://news.google.com/rss/search?q=site:{domain}&hl={lang}&gl={gl}&ceid={ceid}"
        r = requests.get(url, timeout=15)
        feed = feedparser.parse(r.text)
        for entry in feed.entries[:8]:
            title = entry.title
            if title.endswith(f" - {source_name}") or title.endswith(" - Google News"):
                title = title.rsplit(' - ', 1)[0]
            news_list.append({
                "title": title.strip(),
                "link": entry.link,
                "summary": f"{source_name} 官方发布"
            })
    except Exception as e:
        print(f"抓取 {source_name} 失败: {e}")
    return news_list

def fetch_daily_news():
    print("启动直连官方数据源...")
    all_news = {}
    
    # === 平台源 ===
    amazon_news = fetch_amazon_official()
    if amazon_news: all_news["Amazon Seller News"] = amazon_news
        
    tiktok_news = fetch_tiktok_official()
    if tiktok_news: all_news["TikTok Shop Seller"] = tiktok_news
        
    shopify_news = fetch_shopify_changelog()
    if shopify_news: all_news["Shopify Changelog"] = shopify_news
        
    ebay_news = fetch_google_news_rss("sellercenter.ebay.com", "eBay")
    if ebay_news: all_news["eBay Seller Updates"] = ebay_news
        
    walmart_news = fetch_google_news_rss("corporate.walmart.com", "Walmart")
    if walmart_news: all_news["Walmart Release Notes"] = walmart_news
        
    # === 政策源 ===
    federal_news = fetch_federal_register()
    if federal_news: all_news["Federal Register"] = federal_news
        
    gov_uk_news = fetch_gov_uk()
    if gov_uk_news: all_news["GOV.UK"] = gov_uk_news
        
    cbp_news = fetch_google_news_rss("cbp.gov", "CBP")
    if cbp_news: all_news["CBP"] = cbp_news
        
    ustr_news = fetch_google_news_rss("ustr.gov", "USTR")
    if ustr_news: all_news["USTR"] = ustr_news
        
    eu_tax_news = fetch_google_news_rss("taxation-customs.ec.europa.eu", "EU Taxation")
    if eu_tax_news: all_news["EU Taxation"] = eu_tax_news
        
    gacc_news = fetch_google_news_rss("customs.gov.cn", "中国海关总署", "zh-CN", "CN", "CN:zh-Hans")
    if gacc_news: all_news["海关总署"] = gacc_news
        
    mofcom_news = fetch_google_news_rss("mofcom.gov.cn", "中国商务部", "zh-CN", "CN", "CN:zh-Hans")
    if mofcom_news: all_news["商务部"] = mofcom_news
        
    sta_news = fetch_google_news_rss("chinatax.gov.cn", "中国税务总局", "zh-CN", "CN", "CN:zh-Hans")
    if sta_news: all_news["税务总局"] = sta_news
        
    # === 物流源 ===
    usps_news = fetch_google_news_rss("about.usps.com", "USPS")
    if usps_news: all_news["USPS Service Alerts"] = usps_news
        
    dhl_news = fetch_google_news_rss("dhl.com", "DHL")
    if dhl_news: all_news["DHL"] = dhl_news
        
    fedex_news = fetch_google_news_rss("newsroom.fedex.com", "FedEx")
    if fedex_news: all_news["FedEx"] = fedex_news
        
    ups_news = fetch_google_news_rss("about.ups.com", "UPS")
    if ups_news: all_news["UPS"] = ups_news
        
    return all_news

if __name__ == "__main__":
    res = fetch_daily_news()
    for platform, news_list in res.items():
        print(f"--- {platform} ---")
        for item in news_list:
            print(f"- {item['title']}")
