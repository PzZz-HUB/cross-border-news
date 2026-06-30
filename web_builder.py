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
        <title>跨境内参库 Dashboard</title>
        <style>
            :root {
                --primary: #2563eb;
                --bg-main: #f8fafc;
                --text-main: #0f172a;
                --text-muted: #64748b;
                --card-bg: #ffffff;
            }
            body { 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
                background-color: var(--bg-main); 
                color: var(--text-main); 
                margin: 0; 
                padding: 0;
            }
            /* 悬浮顶部导航栏 */
            .navbar {
                position: fixed;
                top: 0; left: 0; right: 0;
                height: 70px;
                background-color: rgba(255, 255, 255, 0.85);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 5%;
                z-index: 1000;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
            }
            .logo { font-size: 22px; font-weight: 800; color: var(--text-main); display: flex; align-items: center; gap: 8px;}
            .search-wrapper { flex: 0 1 400px; position: relative; }
            .search-box { 
                width: 100%; padding: 10px 16px 10px 40px; 
                border: 1px solid #cbd5e1; border-radius: 9999px; 
                font-size: 15px; background-color: #f1f5f9;
                transition: all 0.2s; outline: none;
            }
            .search-box:focus { background-color: #fff; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15); }
            .search-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); font-size: 16px; opacity: 0.5;}
            
            /* 主体内容区 */
            .main-content {
                max-width: 1400px;
                margin: 100px auto 40px;
                padding: 0 5%;
            }
            
            /* 日期分组 */
            .date-group { margin-bottom: 50px; }
            .date-header { 
                font-size: 24px; font-weight: 800; color: var(--text-main); 
                margin-bottom: 24px; display: inline-block;
                position: relative; padding-left: 16px;
            }
            .date-header::before {
                content: ''; position: absolute; left: 0; top: 10%; height: 80%; width: 4px;
                background-color: var(--primary); border-radius: 4px;
            }
            
            /* 网格瀑布流排版 */
            .news-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
                gap: 24px;
            }
            
            /* 新闻卡片 */
            .card { 
                background-color: var(--card-bg); 
                border: 1px solid #e2e8f0; border-radius: 16px; 
                padding: 24px; 
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -2px rgba(0, 0, 0, 0.02); 
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                display: flex; flex-direction: column;
                height: 100%; box-sizing: border-box;
            }
            .card:hover { 
                transform: translateY(-4px); 
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04); 
                border-color: #cbd5e1;
            }
            .card-title { font-size: 17px; font-weight: 700; color: var(--text-main); margin: 0 0 14px 0; line-height: 1.5; }
            .card-title a { color: var(--text-main); text-decoration: none; }
            .card-title a:hover { color: var(--primary); }
            
            .card-summary { 
                font-size: 15px; color: var(--text-muted); line-height: 1.6; margin: 0 0 20px 0; 
                flex-grow: 1; /* 让内容撑开，把底部标签推到底部 */
            }
            
            .card-footer { display: flex; align-items: center; justify-content: space-between; border-top: 1px solid #f1f5f9; padding-top: 16px; }
            .source-tag { font-size: 12px; font-weight: 600; padding: 6px 12px; border-radius: 8px; letter-spacing: 0.5px;}
            
            /* 标签颜色 */
            .tag-36kr { background-color: #fffbeb; color: #b45309; border: 1px solid #fef3c7; }
            .tag-hugo { background-color: #eff6ff; color: #1d4ed8; border: 1px solid #dbeafe; }
            
            .footer { margin-top: 60px; padding: 30px; text-align: center; font-size: 0.9em; color: var(--text-muted); border-top: 1px solid #e2e8f0; }
            .no-results { text-align: center; color: var(--text-muted); padding: 80px 0; font-size: 18px; display: none; }
            
            /* 手机端适配 */
            @media (max-width: 768px) {
                .navbar { padding: 0 20px; flex-direction: column; height: 120px; justify-content: center; gap: 15px; }
                .search-wrapper { flex: none; width: 100%; }
                .main-content { margin-top: 140px; padding: 0 20px; }
                .news-grid { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <!-- 悬浮导航栏 -->
        <nav class="navbar">
            <div class="logo">🌐 跨境内参库</div>
            <div class="search-wrapper">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" class="search-box" placeholder="搜索资讯、平台或关键词..." onkeyup="searchNews()">
            </div>
        </nav>
        
        <div class="main-content">
            <div id="noResults" class="no-results">
                <h2>没有找到相关资讯 💡</h2>
                <p>换个关键词试试吧，比如“亚马逊”或“政策”</p>
            </div>
            
            <div id="newsContainer">
    """
    
    for day_data in archive_data:
        date_str = day_data.get('date', '')
        news_data = day_data.get('news', {})
        
        html += f"""
                <div class="date-group" data-date="{date_str}">
                    <div class="date-header">{date_str}</div>
                    <div class="news-grid">
        """
        
        for source, news_list in news_data.items():
            if not news_list:
                continue
                
            tag_class = "tag-36kr" if "36氪" in source else "tag-hugo"
                
            for item in news_list:
                summary = item.get('summary', '点击查看原文了解详情')
                if not summary.strip():
                    summary = '点击查看原文了解详情'
                title = item.get('title', '')
                
                search_text = f"{title} {summary} {source}".lower().replace('"', '&quot;')
                
                html += f"""
                        <div class="card" data-search="{search_text}">
                            <h2 class="card-title"><a href="{item.get('link', '#')}" target="_blank">{title}</a></h2>
                            <p class="card-summary">{summary}</p>
                            <div class="card-footer">
                                <span class="source-tag {tag_class}">{source}</span>
                            </div>
                        </div>
                """
        
        html += """
                    </div> <!-- end news-grid -->
                </div> <!-- end date-group -->
        """
            
    html += """
            </div>
        </div>
        
        <div class="footer">
            本仪表盘由 AI 自动归档并部署于 GitHub Pages。<br>数据安全持久，永不丢失。
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
                            card.style.display = "flex";
                            hasVisibleCardInGroup = true;
                            hasAnyVisibleCard = true;
                        } else {
                            card.style.display = "none";
                        }
                    }
                    
                    if (hasVisibleCardInGroup) {
                        group.style.display = "block";
                    } else {
                        group.style.display = "none";
                    }
                }
                
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
