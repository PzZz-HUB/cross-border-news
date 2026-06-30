import os
from scraper import fetch_daily_news
from emailer import send_email

def main():
    print("开始抓取最新跨境资讯...")
    news_data = fetch_daily_news()
    
    # 过滤掉空的数据源
    news_data = {k: v for k, v in news_data.items() if v}
    
    if not news_data:
        print("今日未抓取到任何资讯。")
        return
        
    print(f"抓取完成，共 {sum(len(v) for v in news_data.values())} 条新闻。")
    
    # 优先从环境变量获取，如果没有则使用默认配置
    to_email = os.environ.get("TO_EMAIL", "n9_0927@qq.com")
    
    print(f"准备发送邮件至: {to_email}")
    send_email(news_data, to_email)
    
if __name__ == "__main__":
    main()
