import os
import json
import datetime

def load_archive():
    if os.path.exists('data/archive.json'):
        with open('data/archive.json', 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def save_archive(archive_data):
    os.makedirs('data', exist_ok=True)
    with open('data/archive.json', 'w', encoding='utf-8') as f:
        json.dump(archive_data, f, ensure_ascii=False, indent=2)

def generate_html(archive_data):
    html = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>跨境内参库</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f9fafb; color: #333; line-height: 1.6; margin: 0; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; background-color: transparent; }
            .header { text-align: center; padding: 20px 0; margin-bottom: 20px; }
            .header h1 { margin: 0; font-size: 28px; color: #1f2937; font-weight: 800; }
            .search-box { width: 100%; padding: 12px 16px; margin-bottom: 30px; border: 1px solid #d1d5db; border-radius: 12px; font-size: 16px; box-sizing: border-box; box-shadow: 0 1px 2px rgba(0,0,0,0.05); transition: border-color 0.2s; }
            .search-box:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
            
            .date-group { margin-bottom: 40px; }
            .date-header { font-size: 18px; font-weight: 700; color: #4b5563; margin-bottom: 16px; display: flex; align-items: center; }
            .date-header::after { content: ""; flex: 1; height: 1px; background-color: #e5e7eb; margin-left: 12px; }
            
            .card { background-color: #ffffff; border: 1px solid #f3f4f6; border-radius: 16px; padding: 20px; margin-bottom: 16px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.02); transition: transform 0.2s; }
            .card:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08); }
            .card-title { font-size: 17px; font-weight: 600; color: #111827; margin: 0 0 10px 0; line-height: 1.5; }
            .card-title a { color: #1f2937; text-decoration: none; }
            .card-title a:hover { color: #2563eb; }
            .card-summary { font-size: 14px; color: #4b5563; line-height: 1.6; margin: 0 0 16px 0; padding-left: 12px; border-left: 3px solid #3b82f6; background: #f8fafc; padding: 8px 12px; border-radius: 0 8px 8px 0; }
            .card-footer { display: flex; align-items: center; font-size: 12px; }
            .source-tag { background-color: #e0e7ff; color: #4338ca; padding: 4px 10px; border-radius: 9999px; font-weight: 600; }
            
            .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center; font-size: 0.85em; color: #9ca3af; }
            .no-results { text-align: center; color: #6b7280; padding: 40px 0; display: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌐 跨境内参库</h1>
            </div>
            
            <input type="text" id="searchInput" class="search-box" placeholder="搜索资讯、平台或关键词..." onkeyup="searchNews()">
            
            <div id="noResults" class="no-results">没有找到相关的资讯，换个关键词试试吧 💡</div>
            
            <div id="newsContainer">
    """
    
    for day_data in archive_data:
        date_str = day_data.get('date', '')
        news_data = day_data.get('news', {})
        
        html += f"""
                <div class="date-group" data-date="{date_str}">
                    <div class="date-header">{date_str}</div>
        """
        
        for source, news_list in news_data.items():
            if not news_list:
                continue
                
            if "36氪" in source:
                tag_style = "background-color: #fef3c7; color: #b45309;"
            else:
                tag_style = "background-color: #e0e7ff; color: #4338ca;"
                
            for item in news_list:
                summary = item.get('summary', '点击查看原文了解详情')
                title = item.get('title', '')
                
                # 为搜索准备纯文本，转换为小写以实现不区分大小写的搜索
                search_text = f"{title} {summary} {source}".lower().replace('"', '&quot;')
                
                html += f"""
                    <div class="card" data-search="{search_text}">
                        <h2 class="card-title"><a href="{item.get('link', '#')}" target="_blank">{title}</a></h2>
                        <p class="card-summary">{summary}</p>
                        <div class="card-footer">
                            <span class="source-tag" style="{tag_style}">{source}</span>
                        </div>
                    </div>
                """
        
        html += """
                </div>
        """
            
    html += """
            </div>
            
            <div class="footer">
                本网页由 AI 智能驱动，自动归档并部署于 GitHub Pages。<br>
                在上方搜索框输入关键词，即可快速检索历史资讯。
            </div>
        </div>
        
        <script>
            function searchNews() {
                var input = document.getElementById('searchInput').value.toLowerCase();
                var groups = document.getElementsByClassName('date-group');
                var hasAnyVisibleCard = false;
                
                for (var i = 0; i < groups.length; i++) {
                    var group = groups[i];
                    var cards = group.getElementsByClassName('card');
                    var hasVisibleCardInGroup = false;
                    
                    for (var j = 0; j < cards.length; j++) {
                        var card = cards[j];
                        var searchText = card.getAttribute('data-search');
                        
                        if (searchText.indexOf(input) > -1) {
                            card.style.display = "";
                            hasVisibleCardInGroup = true;
                            hasAnyVisibleCard = true;
                        } else {
                            card.style.display = "none";
                        }
                    }
                    
                    // 如果这个日期下没有任何卡片可见，就隐藏整个日期组
                    if (hasVisibleCardInGroup) {
                        group.style.display = "";
                    } else {
                        group.style.display = "none";
                    }
                }
                
                // 显示或隐藏"无结果"提示
                document.getElementById('noResults').style.display = hasAnyVisibleCard ? "none" : "block";
            }
        </script>
    </body>
    </html>
    """
    return html

def build_webpage(today_news_data):
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    archive_data = load_archive()
    
    # 查找今天是否已经有数据，如果有则覆盖，没有则插入到最前面
    existing_idx = -1
    for i, data in enumerate(archive_data):
        if data.get('date') == today_str:
            existing_idx = i
            break
            
    today_entry = {
        'date': today_str,
        'news': today_news_data
    }
    
    if existing_idx >= 0:
        archive_data[existing_idx] = today_entry
    else:
        archive_data.insert(0, today_entry)
        
    # 保存更新后的数据
    save_archive(archive_data)
    
    # 生成网页
    html_content = generate_html(archive_data)
    
    os.makedirs("public", exist_ok=True)
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print("网页生成成功：public/index.html")
