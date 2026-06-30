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
    prompt = "你是一个资深的跨境行业前沿观察家。你的任务是帮我挑选出今天最值得一看的【跨境新鲜事】。\n"
    prompt += "挑选标准：\n"
    prompt += "- 广泛保留所有有价值的新鲜事：只要是与【跨境、出海、外贸、全球化】相关的任何重要资讯（不仅限于跨境电商），只要你认为从业者看了会有启发，就必须保留！\n"
    prompt += "- 坚决剔除：卖课、招商大会、拉群、无价值的服务商引流广告。\n"
    prompt += "- 去除重复：如果有多条新闻说的是同一个事件，只保留最重要的一条。\n"
    prompt += "请必须返回一个严格的 JSON 数组格式（不要加 ```json 代码块，直接返回纯数组）。对于每一条输入的新闻，生成一个对象，包含两个字段：\n"
    prompt += "1. 'judgement': 如果保留则填写 '新闻'，如果剔除则填写 '营销'。\n"
    prompt += "2. 'summary': 如果 judgement 是 '新闻'，请写一句精炼的一句话总结（根据标题合理推测或提炼核心亮点，不要超过30个字）。如果是 '营销'，留空。\n"
    prompt += '示例：[{"judgement": "新闻", "summary": "亚马逊发布最新政策，影响卖家利润。"}, {"judgement": "营销", "summary": ""}]\n\n标题列表：\n'
    
    for idx, item in enumerate(news_list):
        prompt += f"{idx + 1}. {item['title']}\n"
        
    print("正在请求 Gemini AI 进行语义判断...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        import json
        text = response.text.strip()
        if text.startswith("```json"): text = text[7:]
        elif text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        text = text.strip()
        
        results = json.loads(text)
        
        for idx, item in enumerate(news_list):
            if idx < len(results):
                judgement = results[idx].get("judgement", "")
                if "营销" in judgement:
                    print(f"[AI 判定为营销，已剔除]: {item['title']}")
                else:
                    item['summary'] = results[idx].get("summary", "点击查看原文了解详情")
                    filtered_list.append(item)
            else:
                item['summary'] = "点击查看原文了解详情"
                filtered_list.append(item)
                
    except Exception as e:
        print(f"AI 判断过程发生错误: {e}")
        return news_list
        
    return filtered_list
