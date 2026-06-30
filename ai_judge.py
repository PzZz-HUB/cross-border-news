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
    prompt = "你是一个资深的跨境电商媒体主编。你的任务是帮我挑选出今天最值得一看的【跨境新鲜事】。\n"
    prompt += "挑选标准：\n"
    prompt += "- 强烈保留：关于跨境平台政策变化（亚马逊/TikTok等）、什么产品卖得火、海外市场趋势、物流海关新规。\n"
    prompt += "- 坚决剔除：任何卖课、招商大会、拉群、无价值的纯服务商广告。\n"
    prompt += "- 去除重复：如果有多条新闻说的是同一个事件，只保留最重要的一条。\n"
    prompt += "对于每一条，请严格只回复 '新闻' 或 '营销'，按顺序回复，用逗号分隔（如果你觉得某条是重复内容，也请标记为 '营销' 以便剔除）。\n\n标题列表：\n"
    
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
