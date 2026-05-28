import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
import json

# 从根目录导入配置
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, INDUSTRIES

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

def analyze_news(news_list):
    if not news_list:
        return []
    
    batch_size = 6
    results = []
    
    system_prompt = f"""你是一位专注孟加拉国的中国商业情报分析师。
请严格按以下格式输出JSON数组，不要输出其他任何文字：

[{{
  "industry": "必须从以下列表精确选择：{INDUSTRIES}",
  "type": "政策|投资|市场动态|风险|合作",
  "entities": ["实体1", "实体2"],
  "chinese_summary": "150-220字的中文摘要",
  "impact": "正面|中性|负面",
  "importance": "高|中|低",
  "risk_tags": ["风险1", "风险2"],
  "reasoning": "判断依据"
}}]
"""
    
    for i in range(0, len(news_list), batch_size):
        batch = news_list[i:i+batch_size]
        prompt = "请分析以下新闻：\n\n"
        for idx, news in enumerate(batch, 1):
            prompt += f"新闻{idx}：标题：{news['title']}\n摘要：{news.get('summary','')}\n来源：{news['source']}\n\n"
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=3500
            )
            
            content = response.choices[0].message.content.strip()
            # 清理可能的多余标记
            if content.startswith('```json'):
                content = content[7:-3].strip()
            elif content.startswith('```'):
                content = content[3:-3].strip()
            
            batch_result = json.loads(content)
            if isinstance(batch_result, dict):
                results.append(batch_result)
            else:
                results.extend(batch_result)
                
        except Exception as e:
            print(f"AI分析出错: {e}")
            for _ in batch:
                results.append({
                    "industry": "其他",
                    "type": "市场动态",
                    "entities": [],
                    "chinese_summary": "分析失败",
                    "impact": "中性",
                    "importance": "中",
                    "risk_tags": [],
                    "reasoning": str(e)[:100]
                })
    
    return results

if __name__ == "__main__":
    os.makedirs('data', exist_ok=True)
    with open('data/raw_news.json', 'r', encoding='utf-8') as f:
        news = json.load(f)
    analyzed = analyze_news(news)
    with open('data/analyzed_news.json', 'w', encoding='utf-8') as f:
        json.dump(analyzed, f, ensure_ascii=False, indent=2)
    print(f"AI分析完成，共 {len(analyzed)} 条情报")
