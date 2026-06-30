import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import os

def generate_html(news_data):
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 20px auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
            h1 {{ color: #2c3e50; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            .source-title {{ color: #e67e22; font-size: 1.2em; margin-top: 20px; border-left: 4px solid #e67e22; padding-left: 10px; }}
            ul {{ list-style-type: none; padding-left: 0; }}
            li {{ margin-bottom: 10px; padding: 10px; background: #f9f9f9; border-radius: 5px; }}
            a {{ color: #2980b9; text-decoration: none; font-weight: 500; }}
            a:hover {{ text-decoration: underline; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 0.9em; color: #7f8c8d; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 每日跨境资讯 ({today_str})</h1>
    """
    
    for source, news_list in news_data.items():
        if not news_list:
            continue
        html += f"<div class='source-title'>{source}</div><ul>"
        for item in news_list:
            html += f"<li><a href='{item['link']}' target='_blank'>{item['title']}</a></li>"
        html += "</ul>"
        
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
