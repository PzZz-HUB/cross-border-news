import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from scraper import fetch_daily_news

news = fetch_daily_news()
for k, v in news.items():
    print(f"[{k}]")
    for item in v:
        print(f"- {item['title']} ({item['link']})")
