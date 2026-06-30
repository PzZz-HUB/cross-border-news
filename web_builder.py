import os
import datetime

def generate_html(news_data):
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 获取总新闻数
    total_news = sum(len(v) for v in news_data.values())
    
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>每日跨境新鲜事</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #ffffff; color: #333; line-height: 1.6; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
            .header {{ text-align: center; padding: 20px 0; border-bottom: 1px solid #f0f0f0; margin-bottom: 20px; }}
            .header h1 {{ margin: 0; font-size: 24px; color: #1f2937; }}
            .date {{ color: #6b7280; font-size: 14px; margin-top: 5px; }}
            .card {{ background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px -3px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.04); }}
            .card-title {{ font-size: 18px; font-weight: 600; color: #111827; margin: 0 0 10px 0; line-height: 1.4; }}
            .card-title a {{ color: #111827; text-decoration: none; }}
            .card-title a:hover {{ color: #3b82f6; text-decoration: underline; }}
            .card-summary {{ font-size: 15px; color: #4b5563; line-height: 1.6; margin: 0 0 16px 0; padding-left: 12px; border-left: 3px solid #3b82f6; }}
            .card-footer {{ display: flex; align-items: center; font-size: 12px; }}
            .source-tag {{ background-color: #e0e7ff; color: #4338ca; padding: 4px 10px; border-radius: 9999px; font-weight: 500; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #f0f0f0; text-align: center; font-size: 0.9em; color: #7f8c8d; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌐 每日跨境新鲜事</h1>
                <div class="date">{today_str} (今日精选 {total_news} 条)</div>
            </div>
    """
    
    for source, news_list in news_data.items():
        if not news_list:
            continue
            
        # 根据来源使用不同的标签颜色
        if "36氪" in source:
            tag_style = "background-color: #fef3c7; color: #b45309;"
        else:
            tag_style = "background-color: #e0e7ff; color: #4338ca;"
            
        for item in news_list:
            summary = item.get('summary', '点击查看原文了解详情')
            html += f"""
            <div class="card">
                <h2 class="card-title"><a href="{item['link']}" target="_blank">{item['title']}</a></h2>
                <p class="card-summary">{summary}</p>
                <div class="card-footer">
                    <span class="source-tag" style="{tag_style}">{source}</span>
                </div>
            </div>
            """
            
    html += """
            <div class="footer">
                本网页由 AI 智能驱动，代码运行于 GitHub Actions。
            </div>
        </div>
    </body>
    </html>
    """
    return html

def build_webpage(news_data):
    html_content = generate_html(news_data)
    
    # 确保 public 目录存在
    os.makedirs("public", exist_ok=True)
    
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print("网页生成成功：public/index.html")
