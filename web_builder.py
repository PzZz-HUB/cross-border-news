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
                --success: #10b981;
                --error: #ef4444;
                --warning: #f59e0b;
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

            /* Dashboard 面板 */
            .dashboard-panel {
                background: white;
                border-radius: 12px;
                padding: 24px;
                margin-bottom: 40px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            }
            .dashboard-title {
                font-size: 18px; font-weight: 700; margin-top: 0; margin-bottom: 16px;
                display: flex; align-items: center; gap: 8px;
            }
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 12px;
            }
            .status-item {
                display: flex; align-items: center; justify-content: space-between;
                padding: 10px 12px; border-radius: 8px; background: #f8fafc;
                font-size: 14px; border: 1px solid #e2e8f0;
            }
            .status-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 8px; }
            .dot-success { background-color: var(--success); }
            .dot-error { background-color: var(--error); }
            .dot-nodata { background-color: var(--warning); }
            
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
                flex-grow: 1;
            }
            
            .card-footer { display: flex; align-items: center; justify-content: space-between; border-top: 1px solid #f1f5f9; padding-top: 16px; }
            .source-tag { font-size: 12px; font-weight: 600; padding: 6px 12px; border-radius: 8px; letter-spacing: 0.5px;}

            /* 隔离审查区 */
            .review-section {
                margin-top: 80px; padding: 30px; background: #fff5f5; border: 1px solid #fed7d7; border-radius: 12px;
            }
            .review-header { display: flex; align-items: center; justify-content: space-between; cursor: pointer; }
            .review-title { font-size: 18px; font-weight: 700; color: #c53030; margin: 0; display: flex; align-items: center; gap: 8px;}
            .review-content { margin-top: 20px; display: none; }
            .review-item { padding: 12px 16px; border-bottom: 1px solid #fed7d7; font-size: 14px; }
            .review-item:last-child { border-bottom: none; }
            .review-reason { display: inline-block; padding: 2px 8px; background: #fed7d7; color: #9b2c2c; border-radius: 4px; font-size: 12px; margin-right: 12px; font-weight: 600; }
            
            .footer { margin-top: 60px; padding: 30px; text-align: center; font-size: 0.9em; color: var(--text-muted); border-top: 1px solid #e2e8f0; }
            .no-results { text-align: center; color: var(--text-muted); padding: 80px 0; font-size: 18px; display: none; }
            
            @media (max-width: 768px) {
                .navbar { padding: 0 20px; flex-direction: column; height: 120px; justify-content: center; gap: 15px; }
                .search-wrapper { flex: none; width: 100%; }
                .main-content { margin-top: 140px; padding: 0 20px; }
                .news-grid { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
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
        quarantined_data = day_data.get('quarantined', [])
        statuses = day_data.get('statuses', {})
        
        html += f"""
                <div class="date-group" data-date="{date_str}">
                    <div class="date-header">{date_str}</div>
        """

        # Dashboard for today
        if statuses:
            html += """
                    <div class="dashboard-panel">
                        <h3 class="dashboard-title">📡 系统运行大盘 (抓取节点状态)</h3>
                        <div class="status-grid">
            """
            for source, status_info in statuses.items():
                s = status_info.get("status", "Unknown")
                c = status_info.get("count", 0)
                if s == "OK":
                    dot_class = "dot-success"
                    text = f"✅ {c} 条"
                elif s == "No Data Today":
                    dot_class = "dot-nodata"
                    text = "⚪ 无更新"
                else:
                    dot_class = "dot-error"
                    text = "❌ 失败"
                html += f"""
                            <div class="status-item">
                                <div><span class="status-dot {dot_class}"></span><strong>{source}</strong></div>
                                <span>{text}</span>
                            </div>
                """
            html += """
                        </div>
                    </div>
            """

        html += """
                    <div class="news-grid">
        """
        
        for source, news_list in news_data.items():
            if not news_list:
                continue
                
            source_lower = source.lower()
            if "amazon" in source_lower or "亚马逊" in source_lower:
                tag_style = "background-color: #fff7ed; color: #c2410c; border: 1px solid #ffedd5;"
            elif "tiktok" in source_lower:
                tag_style = "background-color: #f8fafc; color: #0f172a; border: 1px solid #cbd5e1;"
            elif "shopee" in source_lower or "虾皮" in source_lower:
                tag_style = "background-color: #fff1f2; color: #be123c; border: 1px solid #ffe4e6;"
            elif "temu" in source_lower:
                tag_style = "background-color: #fdf4ff; color: #a21caf; border: 1px solid #fae8ff;"
            else:
                tag_style = "background-color: #eff6ff; color: #1d4ed8; border: 1px solid #dbeafe;"
                
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
                                <span class="source-tag" style="{tag_style}">{source}</span>
                            </div>
                        </div>
                """
        
        html += """
                    </div> <!-- end news-grid -->
        """

        # Quarantine Zone for today
        if quarantined_data:
            html += f"""
                    <div class="review-section">
                        <div class="review-header" onclick="toggleReview(this)">
                            <h3 class="review-title">🗑️ 隔离审查区 ({len(quarantined_data)} 条被剔除资讯)</h3>
                            <span>▼ 点击展开/收起</span>
                        </div>
                        <div class="review-content">
            """
            for q in quarantined_data:
                reason = q.get('reject_reason', 'Unknown')
                title = q.get('title', '')
                src = q.get('source', '')
                html += f"""
                            <div class="review-item">
                                <span class="review-reason">{reason}</span>
                                <strong>[{src}]</strong> {title}
                            </div>
                """
            html += """
                        </div>
                    </div>
            """

        html += """
                </div> <!-- end date-group -->
        """
            
    html += """
            </div>
        </div>
        
        <div class="footer">
            本仪表盘数据直接抓取自跨境平台官方官网（Newsroom）。<br>100% 官方原汁原味，无第三方加工，数据安全持久。
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
            
            function toggleReview(element) {
                var content = element.nextElementSibling;
                if (content.style.display === "block") {
                    content.style.display = "none";
                } else {
                    content.style.display = "block";
                }
            }
        </script>
    </body>
    </html>
    """
    return html

def build_webpage(today_news_data, quarantined_news, source_statuses):
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    archive_data = load_archive()
    
    existing_idx = -1
    for i, data in enumerate(archive_data):
        if data.get('date') == today_str:
            existing_idx = i
            break
            
    today_entry = {
        'date': today_str,
        'news': today_news_data,
        'quarantined': quarantined_news,
        'statuses': source_statuses
    }
    
    if existing_idx >= 0:
        archive_data[existing_idx] = today_entry
    else:
        archive_data.insert(0, today_entry)
        
    save_archive(archive_data)
    
    html_content = generate_html(archive_data)
    
    os.makedirs("public", exist_ok=True)
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print("网页生成成功：public/index.html")
