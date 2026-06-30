import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import os

def generate_html(news_data):
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 获取总新闻数
    total_news = sum(len(v) for v in news_data.values())
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f3f4f6; color: #333; line-height: 1.6; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #f3f4f6; }}
            .header {{ text-align: center; padding: 20px 0; }}
            .header h1 {{ margin: 0; font-size: 24px; color: #1f2937; }}
            .date {{ color: #6b7280; font-size: 14px; margin-top: 5px; }}
            .card {{ background-color: #ffffff; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
            .card-title {{ font-size: 18px; font-weight: 600; color: #111827; margin: 0 0 10px 0; line-height: 1.4; }}
            .card-title a {{ color: #111827; text-decoration: none; }}
            .card-title a:hover {{ color: #3b82f6; text-decoration: underline; }}
            .card-summary {{ font-size: 15px; color: #4b5563; line-height: 1.6; margin: 0 0 16px 0; padding-left: 12px; border-left: 3px solid #3b82f6; }}
            .card-footer {{ display: flex; align-items: center; font-size: 12px; }}
            .source-tag {{ background-color: #e0e7ff; color: #4338ca; padding: 4px 10px; border-radius: 9999px; font-weight: 500; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 0.9em; color: #7f8c8d; }}
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
                本邮件由你的专属跨境资讯小助手自动生成，代码运行于 GitHub Actions。
            </div>
        </div>
    </body>
    </html>
    """
    return html

def send_email(news_data, to_email):
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.qq.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 465))
    from_email = os.environ.get("SMTP_USER", "")
    password = os.environ.get("SMTP_PASS", "")  # 授权码
    
    if not from_email or not password:
        print("未配置发件邮箱账号密码，仅在本地生成 HTML 预览文件 (news_preview.html)，不发送邮件。")
        with open("news_preview.html", "w", encoding="utf-8") as f:
            f.write(generate_html(news_data))
        return
        
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = f"【每日跨境资讯】{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    html_content = generate_html(news_data)
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    try:
        print(f"正在连接 SMTP 服务器 {smtp_server}:{smtp_port}...")
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        print(f"邮件已成功发送至 {to_email}")
    except Exception as e:
        print(f"发送邮件失败: {e}")
