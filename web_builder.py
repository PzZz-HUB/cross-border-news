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
                --neutral: #94a3b8;
            }
            body { 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
                background-color: var(--bg-main); 
                color: var(--text-main); 
                margin: 0; 
                padding: 0;
            }
            .navbar {
                position: fixed; top: 0; left: 0; right: 0; height: 70px;
                background-color: rgba(255, 255, 255, 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
                border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between;
                padding: 0 5%; z-index: 1000; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
            }
            .logo { font-size: 22px; font-weight: 800; color: var(--text-main); display: flex; align-items: center; gap: 8px;}
            .search-wrapper { flex: 0 1 400px; position: relative; }
            .search-box { 
                width: 100%; padding: 10px 16px 10px 40px; 
                border: 1px solid #cbd5e1; border-radius: 9999px; font-size: 15px; background-color: #f1f5f9; outline: none;
            }
            .search-box:focus { background-color: #fff; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15); }
            .search-icon { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); font-size: 16px; opacity: 0.5;}
            
            .main-content { max-width: 1400px; margin: 100px auto 40px; padding: 0 5%; }

            /* Dashboard 面板 */
            .dashboard-panel { background: white; border-radius: 12px; padding: 24px; margin-bottom: 40px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); }
            .dashboard-title { font-size: 18px; font-weight: 700; margin-top: 0; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
            .status-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
            .status-item { padding: 12px 16px; border-radius: 8px; background: #f8fafc; font-size: 14px; border: 1px solid #e2e8f0; }
            .status-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px dashed #cbd5e1; padding-bottom: 8px;}
            .status-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 8px; }
            
            .dot-ok_with_confirmed { background-color: var(--success); }
            .dot-ok_all_quarantined { background-color: var(--warning); }
            .dot-ok_no_candidates { background-color: var(--neutral); }
            .dot-error { background-color: var(--error); }
            
            .funnel-stats { font-size: 12px; color: var(--text-muted); display: flex; justify-content: space-between; line-height: 1.6;}
            .funnel-error { color: var(--error); font-size: 12px; margin-top: 4px; word-break: break-all;}

            /* 日期分组 */
            .date-group { margin-bottom: 50px; }
            .date-header { font-size: 24px; font-weight: 800; color: var(--text-main); margin-bottom: 24px; display: inline-block; position: relative; padding-left: 16px; }
            .date-header::before { content: ''; position: absolute; left: 0; top: 10%; height: 80%; width: 4px; background-color: var(--primary); border-radius: 4px; }
            
            /* 网格瀑布流排版 */
            .news-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 24px; }
            .card { background-color: var(--card-bg); border: 1px solid #e2e8f0; border-radius: 16px; padding: 24px; display: flex; flex-direction: column; height: 100%; box-sizing: border-box; }
            .card:hover { transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.08); border-color: #cbd5e1; }
            .card-title { font-size: 17px; font-weight: 700; color: var(--text-main); margin: 0 0 14px 0; line-height: 1.5; }
            .card-title a { color: var(--text-main); text-decoration: none; }
            .card-title a:hover { color: var(--primary); }
            .card-summary { font-size: 15px; color: var(--text-muted); line-height: 1.6; margin: 0 0 20px 0; flex-grow: 1; }
            .card-footer { display: flex; align-items: center; justify-content: space-between; border-top: 1px solid #f1f5f9; padding-top: 16px; }
            .source-tag { font-size: 12px; font-weight: 600; padding: 6px 12px; border-radius: 8px; }

            /* 隔离审查区 */
            .review-section { margin-top: 80px; padding: 24px; background: #fff5f5; border: 1px solid #fed7d7; border-radius: 12px; }
            .review-header { display: flex; align-items: center; justify-content: space-between; cursor: pointer; }
            .review-title { font-size: 18px; font-weight: 700; color: #c53030; margin: 0; }
            
            .review-content { margin-top: 20px; display: none; }
            .review-source-group { margin-bottom: 24px; background: white; border-radius: 8px; border: 1px solid #fecaca; overflow: hidden; }
            .review-source-title { background: #fee2e2; padding: 10px 16px; font-weight: 700; font-size: 15px; color: #991b1b; }
            .review-item { padding: 12px 16px; border-bottom: 1px solid #fee2e2; font-size: 14px; display: flex; flex-direction: column; gap: 8px;}
            .review-item:last-child { border-bottom: none; }
            .review-meta { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
            .review-reason { padding: 2px 8px; background: #fecaca; color: #991b1b; border-radius: 4px; font-size: 12px; font-weight: 600; }
            .review-rule { padding: 2px 8px; background: #e2e8f0; color: #475569; border-radius: 4px; font-size: 12px; }
            .review-link { font-weight: 600; color: #1f2937; text-decoration: none; }
            .review-link:hover { text-decoration: underline; }
            .show-more-btn { width: 100%; text-align: center; padding: 12px; background: #f8fafc; border: none; border-top: 1px solid #fee2e2; color: #3b82f6; cursor: pointer; font-weight: 600; }
            .show-more-btn:hover { background: #f1f5f9; }

            .footer { margin-top: 60px; padding: 30px; text-align: center; font-size: 0.9em; color: var(--text-muted); border-top: 1px solid #e2e8f0; }
            .no-results { text-align: center; color: var(--text-muted); padding: 80px 0; font-size: 18px; display: none; }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <div class="logo">🌐 跨境内参库</div>
            <div class="search-wrapper">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" class="search-box" placeholder="搜索资讯..." onkeyup="searchNews()">
            </div>
        </nav>
        
        <div class="main-content">
            <div id="noResults" class="no-results">
                <h2>没有找到相关资讯 💡</h2>
            </div>
            
            <div id="newsContainer">
    """
    
    for day_data in archive_data:
        date_str = day_data.get('date', '')
        news_data = day_data.get('news', {})
        quarantined_data = day_data.get('quarantined', {}) # Now it's grouped by source!
        statuses = day_data.get('statuses', {})
        summary = day_data.get('summary', {})
        
        html += f"""
                <div class="date-group" data-date="{date_str}">
                    <div class="date-header">{date_str}</div>
        """

        # Dashboard for today
        if statuses:
            html += """
                    <div class="dashboard-panel">
                        <h3 class="dashboard-title">📡 系统运行大盘 (节点全景监控)</h3>
                        <div class="status-grid">
            """
            for source, stat in statuses.items():
                s = stat.get("status", "error")
                dot_class = f"dot-{s}"
                if s == "ok_with_confirmed": text = "✅ 成功 (含核心)"
                elif s == "ok_all_quarantined": text = "🟡 成功 (全隔离)"
                elif s == "ok_no_candidates": text = "⚪ 成功 (无数据)"
                else: text = "❌ 失败"
                
                html += f"""
                            <div class="status-item">
                                <div class="status-header">
                                    <div><span class="status-dot {dot_class}"></span><strong>{source}</strong></div>
                                    <span>{text}</span>
                                </div>
                                <div class="funnel-stats">
                                    <span>初筛: {stat.get('candidates_found', 0)}</span>
                                    <span>丢弃: {stat.get('dropped_count', 0)}</span>
                                    <span style="color:var(--warning)">隔离: {stat.get('quarantined_count', 0)}</span>
                                    <span style="color:var(--success); font-weight:600;">入库: {stat.get('confirmed_count', 0)}</span>
                                </div>
                """
                if stat.get('error_message'):
                    html += f'<div class="funnel-error">{stat.get("error_message")}</div>'
                html += "</div>"
                
            html += """
                        </div>
                    </div>
            """

        html += """
                    <div class="news-grid">
        """
        
        for source, news_list in news_data.items():
            if not news_list: continue
            for item in news_list:
                title = item.get('title', '')
                summary_text = item.get('summary', '')
                link = item.get('link', '#')
                html += f"""
                        <div class="card" data-search="{title.lower()} {source.lower()}">
                            <h2 class="card-title"><a href="{link}" target="_blank">{title}</a></h2>
                            <p class="card-summary">{summary_text}</p>
                            <div class="card-footer">
                                <span class="source-tag" style="background:#eff6ff; color:#1d4ed8;">{source}</span>
                            </div>
                        </div>
                """
        
        html += """
                    </div> <!-- end news-grid -->
        """

        # Quarantine Zone
        if quarantined_data:
            total_q = sum(len(items) for items in quarantined_data.values())
            html += f"""
                    <div class="review-section">
                        <div class="review-header" onclick="toggleReview(this)">
                            <h3 class="review-title">🗑️ 隔离审查区 ({total_q} 条候选资讯未通过最终规则)</h3>
                            <span>▼ 点击展开/收起</span>
                        </div>
                        <div class="review-content">
            """
            for source, q_list in quarantined_data.items():
                if not q_list: continue
                html += f"""
                            <div class="review-source-group">
                                <div class="review-source-title">{source} ({len(q_list)} 条)</div>
                """
                for idx, q in enumerate(q_list):
                    hidden = 'style="display:none;" class="hidden-review-item"' if idx >= 5 else ''
                    html += f"""
                                <div class="review-item" {hidden}>
                                    <div><a class="review-link" href="{q.get('link', '#')}" target="_blank">{q.get('title', '')}</a></div>
                                    <div class="review-meta">
                                        <span class="review-reason">判定理由: {q.get('reject_reason', 'Unknown')}</span>
                                        <span class="review-rule">触发规则: {q.get('rule_triggered', 'Unknown')}</span>
                                        <span style="color:#64748b; font-size:12px;">{q.get('pub_time', '')}</span>
                                    </div>
                                </div>
                    """
                if len(q_list) > 5:
                    html += f"""
                                <button class="show-more-btn" onclick="showMore(this)">展开全部 {len(q_list)} 条 ▾</button>
                    """
                html += "</div>"
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
                    group.style.display = hasVisibleCardInGroup ? "block" : "none";
                }
                document.getElementById('noResults').style.display = hasAnyVisibleCard ? "none" : "block";
            }
            
            function toggleReview(element) {
                var content = element.nextElementSibling;
                content.style.display = (content.style.display === "block") ? "none" : "block";
            }
            
            function showMore(btn) {
                var group = btn.parentElement;
                var hiddenItems = group.querySelectorAll('.hidden-review-item');
                hiddenItems.forEach(function(item) {
                    item.style.display = "flex";
                });
                btn.style.display = "none";
            }
        </script>
    </body>
    </html>
    """
    return html

def build_webpage():
    report_path = "data/latest/run_report.json"
    if not os.path.exists(report_path):
        print(f"找不到运行报告 {report_path}，跳过生成网页。")
        return
        
    with open(report_path, "r", encoding="utf-8") as f:
        run_report = json.load(f)
        
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    archive_data = load_archive()
    
    existing_idx = -1
    for i, data in enumerate(archive_data):
        if data.get('date') == today_str:
            existing_idx = i
            break
            
    today_entry = {
        'date': today_str,
        'news': run_report.get('confirmed_news', {}),
        'quarantined': run_report.get('quarantined_news', {}),
        'statuses': run_report.get('source_statuses', {}),
        'summary': run_report.get('summary', {})
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

if __name__ == "__main__":
    build_webpage()
