import os
from google import genai
from google.genai import types

def filter_news_with_ai(news_list):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("未配置 GEMINI_API_KEY，跳过 AI 判断，保留所有初步筛选的新闻。")
        return news_list
        
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"初始化 Gemini Client 失败: {e}")
        return news_list
        
    filtered_list = []
    
    # 批量判断为了省时间，我们把所有标题合并成一个 Prompt 发给 AI
    prompt = "你是一个极度严格的跨境电商官方政策提取器。\n"
    prompt += "你的唯一任务是：从以下新闻列表中，精准提取出【跨境电商平台（如亚马逊、TikTok、Shopee等）发布的官方公告、最新政策、费率变动、功能上线】。\n"
    prompt += "挑选标准：\n"
    prompt += "- 必须保留：任何具有官方性质的平台规则变化、后台系统更新、关税政策变动。\n"
    prompt += "- 坚决剔除：所有第三方的分析文章、卖家故事、行业趋势预测、服务商广告、招商大会、以及任何非官方的“小道消息”。哪怕它写得再好，只要不是官方动作，一律剔除！\n"
    prompt += "- 去除重复：如果有多条新闻说的是同一个官方公告，只保留最核心的一条。\n"
    prompt += "请必须返回一个严格的 JSON 数组格式（不要加 ```json 代码块，直接返回纯数组）。对于每一条输入的新闻，生成一个对象，包含两个字段：\n"
    prompt += "1. 'judgement': 如果保留则填写 '官方公告'，如果剔除则填写 '无效信息'。\n"
    prompt += "2. 'summary': 如果 judgement 是 '官方公告'，请写一句精炼的一句话总结（提炼政策的核心要点，不要超过30个字）。如果是 '无效信息'，留空。\n"
    prompt += '示例：[{"judgement": "官方公告", "summary": "亚马逊更新FBA退货政策，要求卖家在30天内处理。"}, {"judgement": "无效信息", "summary": ""}]\n\n标题列表：\n'
    
    for idx, item in enumerate(news_list):
        prompt += f"{idx + 1}. {item['title']}\n"
        
    print("正在请求 Gemini AI 进行语义判断...")
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        import json
        text = response.text.strip()
        
        # 寻找JSON数组的起始和结束位置，防止包含额外的文字
        start_idx = text.find('[')
        end_idx = text.rfind(']')
        if start_idx != -1 and end_idx != -1:
            text = text[start_idx:end_idx+1]
            
        results = json.loads(text)
        
        for idx, item in enumerate(news_list):
            if idx < len(results):
                judgement = results[idx].get("judgement", "")
                if "无效信息" in judgement:
                    print(f"[AI 判定为无效信息，已剔除]: {item['title']}")
                else:
                    item['summary'] = results[idx].get("summary", "点击查看原文了解详情")
                    filtered_list.append(item)
            else:
                item['summary'] = "点击查看原文了解详情"
                filtered_list.append(item)
                
    except Exception as e:
        print(f"AI 接口调用或解析发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        try:
            print(f"API返回的原始文本为: {response.text}")
        except:
            pass
        return news_list
        
    return filtered_list
