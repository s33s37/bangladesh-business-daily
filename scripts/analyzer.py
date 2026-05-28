from openai import OpenAI
import json
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, INDUSTRIES

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

def analyze_news(news_list):
    if not news_list:
        return []
    
    batch_size = 6
    results = []
    
    system_prompt = f"""你是一位专注孟加拉国的中国商业情报分析师。
请为每条新闻按以下JSON格式严格输出（不要输出其他内容）：

{{
  "industry": "必须从以下列表中精确选择一个：{INDUSTRIES}",
  "type": "政策|投资|市场动态|风险|合作",
  "entities": ["实体1", "实体2"],
  "chinese_summary": "150-220字的中文专业摘要",
  "impact": "正面|中性|负面",
  "importance": "高|中|低",
  "risk_tags": ["风险标签1", "风险标签2"],
  "reasoning": "简要判断依据"
}}

只返回合法JSON数组。
"""
    
    for i in range(0, len(news_list), batch_size):
        batch = news_list[i:i+batch_size]
        prompt = "请分析以下孟加拉国新闻：\n\n"
        for idx, news in enumerate(batch):
            prompt += f"新闻{idx+1}：\n标题：{news['title']}\n摘要：{news.get('summary','')}\n来源：{news['source']}\n\n"
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3].strip()
            elif content.startswith('```'):
                content = content[3:-3].strip()
            
            analyzed_batch = json.loads(content)
            results.extend(analyzed_batch)
            
        except Exception as e:
            print(f"AI分析出错: {e}")
            for _ in batch:
                results.append({
                    "industry": "其他",
                    "type": "市场动态",
                    "entities": [],
                    "chinese_summary": "AI分析失败，使用原始标题",
                    "impact": "中性",
                    "importance": "中",
                    "risk_tags": [],
                    "reasoning": "解析失败"
                })
    
    return results

if __name__ == "__main__":
    with open('data/raw_news.json', 'r', encoding='utf-8') as f:
        news = json.load(f)
    analyzed = analyze_news(news)
    with open('data/analyzed_news.json', 'w', encoding='utf-8') as f:
        json.dump(analyzed, f, ensure_ascii=False, indent=2)
    print(f"完成AI分析，共 {len(analyzed)} 条情报")
