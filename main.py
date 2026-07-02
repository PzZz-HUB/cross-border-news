import os
import sys
import json
import datetime
import google.generativeai as genai
from scraper import fetch_daily_news
from web_builder import build_webpage

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

AUTO_KEEP = ["Shopify Changelog", "eBay Seller Updates", "CBP", "USTR"]
TRUSTED_RULE = ["Federal Register", "GOV.UK", "EU Taxation"]
TRUSTED_KEYWORDS = ["tariff", "tax", "trade", "custom", "import", "export", "ecommerce", "seller", "shipping", "freight", "logistic", "border", "duty", "rule", "amendment", "regulation"]

def check_trusted_rule(title):
    title_lower = title.lower()
    for kw in TRUSTED_KEYWORDS:
        if kw in title_lower:
            return True, f"命中业务关键词: {kw}", "weak_match"
    return False, "未命中任何跨境业务关键词", "non_seller_news"

def ai_is_relevant(title):
    # 1. 极速本地黑名单过滤
    blacklist = ["党建", "周年", "庆典", "合唱", "歌曲", "红船谣", "党委", "纪委", "党支部", "党课", "晚会", "歌咏", "比赛", "走访慰问", "离退休"]
    for word in blacklist:
        if word in title:
            return False, f"触发关键词: {word}", "blacklist"

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(f" [警告] 未配置 GEMINI_API_KEY，默认通过此新闻: {title}")
        return True, "API Key Missing, Default Pass", "ai_bypass"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
你是一个无情的二极管过滤器。以下是一条电商平台或政府发布的官方新闻标题：
"{title}"
请判断这条新闻是否与【跨境电商卖家】有关（比如关税、平台政策、运营更新、物流变动）。
如果它纯粹是企业内部事件、国家庆典或娱乐（比如高管变动、慈善捐款、颁奖典礼、社区服务、晚会、党建、歌曲、合唱等）请判断为无关。
只需要回答 True 或者 False，不要回答任何其他多余的字。
"""
        response = model.generate_content(prompt)
        text = response.text.strip().lower()
        if text.startswith('false') or 'false' in text:
            return False, "判定为无关公关稿", "ai"
        return True, "AI 判定通过", "ai"
    except Exception as e:
        print(f"AI 过滤请求失败，默认通过 ({title}): {e}")
        return True, f"AI Error: {e}", "ai_error"

def process_data():
    print("开始执行每日资讯收集任务...")
    news_data, fetch_statuses = fetch_daily_news()
    
    run_report = {
        "run_at": datetime.datetime.now().isoformat(),
        "source_statuses": {},
        "raw_candidates": 0,
        "confirmed_news": {},
        "quarantined_news": {},
        "dropped_items": 0,
        "summary": {}
    }
    
    total_confirmed = 0
    total_quarantined = 0
    total_dropped = 0
    
    # Initialize statuses
    for src, status_info in fetch_statuses.items():
        run_report["source_statuses"][src] = {
            "candidates_found": status_info.get("count", 0),
            "confirmed_count": 0,
            "quarantined_count": 0,
            "dropped_count": 0,
            "error_message": status_info.get("status") if "Error" in status_info.get("status", "") else None,
            "last_run_at": run_report["run_at"],
            "status": "error" if "Error" in status_info.get("status", "") else "ok_no_candidates"
        }
        run_report["raw_candidates"] += status_info.get("count", 0)
        
    for source, articles in news_data.items():
        seen_titles = set()
        for a in articles:
            title = a.get('title', '').strip()
            link = a.get('link', '').strip()
            
            # Dropped Check (empty, duplicate)
            if not title or not link or title in seen_titles:
                run_report["source_statuses"][source]["dropped_count"] += 1
                total_dropped += 1
                continue
                
            seen_titles.add(title)
            
            is_rel = False
            reason = ""
            rule = ""
            
            # Auto Keep
            if source in AUTO_KEEP:
                is_rel, reason, rule = True, "源端白名单直通", "auto_keep"
            # Trusted Rule
            elif source in TRUSTED_RULE:
                is_rel, reason, rule = check_trusted_rule(title)
            # Mixed (AI & Blacklist)
            else:
                is_rel, reason, rule = ai_is_relevant(title)
                
            a['reject_reason'] = reason
            a['rule_triggered'] = rule
            a['source'] = source
            a['pub_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if is_rel:
                run_report["confirmed_news"].setdefault(source, []).append(a)
                run_report["source_statuses"][source]["confirmed_count"] += 1
                total_confirmed += 1
            else:
                run_report["quarantined_news"].setdefault(source, []).append(a)
                run_report["source_statuses"][source]["quarantined_count"] += 1
                total_quarantined += 1

    # Finalize statuses
    for src, stat in run_report["source_statuses"].items():
        if stat["error_message"]:
            stat["status"] = "error"
        elif stat["confirmed_count"] > 0:
            stat["status"] = "ok_with_confirmed"
        elif stat["quarantined_count"] > 0:
            stat["status"] = "ok_all_quarantined"
        else:
            stat["status"] = "ok_no_candidates"

    run_report["summary"] = {
        "total_confirmed": total_confirmed,
        "total_quarantined": total_quarantined,
        "total_dropped": total_dropped
    }
    
    os.makedirs("data/latest", exist_ok=True)
    with open("data/latest/run_report.json", "w", encoding="utf-8") as f:
        json.dump(run_report, f, ensure_ascii=False, indent=2)
        
    print(f"数据清洗完毕，报告已生成 data/latest/run_report.json")
    print(f"有效: {total_confirmed}, 隔离: {total_quarantined}, 丢弃: {total_dropped}")

def main():
    process_data()
    build_webpage()

if __name__ == "__main__":
    main()
