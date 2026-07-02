import requests
import feedparser
import datetime
import time

def is_today_utc8(parsed_time):
    if not parsed_time:
        return False
    # 获取发布时间的 datetime 对象
    dt = datetime.datetime.fromtimestamp(time.mktime(parsed_time))
    # 转换为 UTC+8 (东八区时间)
    utc_dt = datetime.datetime.utcfromtimestamp(time.mktime(parsed_time))
    bj_dt = utc_dt + datetime.timedelta(hours=8)
    
    # 获取当前东八区时间
    now_utc = datetime.datetime.utcnow()
    now_bj = now_utc + datetime.timedelta(hours=8)
    
    # 比较日期是否是今天
    return bj_dt.date() == now_bj.date()

def fetch_federal_register():
    print("正在抓取 Federal Register 官方 API...")
    news_list = []
    try:
        r = requests.get("https://www.federalregister.gov/api/v1/documents.json?conditions[type][]=NOTICE&per_page=8", timeout=15)
        data = r.json()
        now_bj = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        today_str = now_bj.strftime('%Y-%m-%d')
        
        for item in data.get('results', []):
            pub_date = item.get('publication_date')
            if pub_date == today_str:
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
        for entry in feed.entries:
            if is_today_utc8(entry.published_parsed):
                news_list.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": "Shopify 官方发布"
                })
                if len(news_list) >= 8: break
    except Exception as e:
        print(f"抓取 Shopify 失败: {e}")
    return news_list

def fetch_gov_uk():
    print("正在抓取 GOV.UK (英国政府) 通告...")
    news_list = []
    try:
        r = requests.get("https://www.gov.uk/search/news-and-communications.atom", timeout=15)
        feed = feedparser.parse(r.text)
        for entry in feed.entries:
            time_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
            if is_today_utc8(time_parsed):
                news_list.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": "GOV.UK 官方通告"
                })
                if len(news_list) >= 8: break
    except Exception as e:
        print(f"抓取 GOV.UK 失败: {e}")
    return news_list

def fetch_google_news_rss(domain, source_name, lang="en-US", gl="US", ceid="US:en"):
    print(f"正在通过官方索引抓取 {source_name}...")
    news_list = []
    try:
        url = f"https://news.google.com/rss/search?q=site:{domain}+when:1d&hl={lang}&gl={gl}&ceid={ceid}"
        r = requests.get(url, timeout=15)
        feed = feedparser.parse(r.text)
        for entry in feed.entries:
            if is_today_utc8(entry.published_parsed):
                title = entry.title
                if title.endswith(f" - {source_name}") or title.endswith(" - Google News"):
                    title = title.rsplit(' - ', 1)[0]
                news_list.append({
                    "title": title.strip(),
                    "link": entry.link,
                    "summary": f"{source_name} 官方发布"
                })
                if len(news_list) >= 8: break
    except Exception as e:
        print(f"抓取 {source_name} 失败: {e}")
    return news_list

def fetch_daily_news():
    print("启动直连官方数据源 (仅筛选今天当天的新闻)...")
    all_news = {}
    
    # === 平台源 ===
    amazon_news = fetch_google_news_rss("aboutamazon.com/news", "Amazon")
    if amazon_news: all_news["Amazon Seller News"] = amazon_news
        
    tiktok_news = fetch_google_news_rss("newsroom.tiktok.com", "TikTok")
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
    news = fetch_daily_news()
    for source, articles in news.items():
        print(f"\n{source}:")
        for a in articles:
            print(f"  - {a['title']}")
