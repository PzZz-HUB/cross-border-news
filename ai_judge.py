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
    prompt = "你是一个资深的跨境电商媒体主编。你的任务是帮我过滤掉明显的【垃圾广告】，但必须保留【行业干货】。\n"
    prompt += "判断标准：\n"
    prompt += "- 如果标题是行业新闻、政策解读、实操干货、选品指南、避坑指南，请判定为 '新闻'。\n"
    prompt += "- 仅当标题【明确表现出强烈的卖课、拉群引流、收费服务商广告】时，才判定为 '营销'。\n"
    prompt += "- 宁可错放，绝不错杀！只要它可能对跨境卖家有一丁点用，就必须是 '新闻'。\n"
    prompt += "对于每一条，请严格只回复 '新闻' 或 '营销'，按顺序回复，用逗号分隔。\n\n标题列表：\n"
    
    for idx, item in enumerate(news_list):
        prompt += f"{idx + 1}. {item['title']}\n"
        
    print("正在请求 Gemini AI 进行语义判断...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        # 解析 AI 的回复
        results = response.text.replace("\n", ",").replace("，", ",").split(",")
        # 清理空格和空字符串
        results = [r.strip() for r in results if r.strip()]
        
        for idx, item in enumerate(news_list):
            if idx < len(results):
                judgement = results[idx]
                if "营销" in judgement:
                    print(f"[AI 判定为营销，已剔除]: {item['title']}")
                else:
                    filtered_list.append(item)
            else:
                # 如果 AI 返回的数量不够，默认保留
                filtered_list.append(item)
                
    except Exception as e:
        print(f"AI 判断过程发生错误: {e}")
        return news_list
        
    return filtered_list
