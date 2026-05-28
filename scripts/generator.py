from jinja2 import Template
import json
from datetime import datetime
import pytz
import os
from config import REPORT_TITLE

def generate_html_report():
    # 强制读取最新分析结果
    json_path = 'data/analyzed_news.json'
    if not os.path.exists(json_path):
        print("错误：analyzed_news.json 不存在")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"生成HTML时读取到 {len(data)} 条情报")
    
    # 统计数据
    total = len(data)
    risk_count = sum(1 for item in data if item.get('impact') == '负面' or any('风险' in str(tag) for tag in item.get('risk_tags', [])))
    policy_count = sum(1 for item in data if item.get('type') == '政策')
    positive_count = sum(1 for item in data if item.get('impact') == '正面')
    
    # 按产业分组
    from collections import defaultdict
    industry_data = defaultdict(list)
    for item in data:
        industry = item.get('industry', '其他')
        industry_data[industry].append(item)
    
    beijing_time = datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y年%m月%d日")
    
    html_template = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ title }} - {{ date }}</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .tag-positive { background: #22c55e; color: white; }
            .tag-negative { background: #ef4444; color: white; }
            .tag-neutral { background: #64748b; color: white; }
            .tag-risk { background: #f59e0b; color: white; }
            .card-hover:hover { transform: translateY(-4px); transition: all 0.3s; }
        </style>
    </head>
    <body class="bg-gray-50 font-sans">
        <div class="max-w-7xl mx-auto p-6">
            <div class="text-center mb-8">
                <h1 class="text-4xl font-bold text-gray-900">{{ title }}</h1>
                <p class="text-gray-600 mt-2">{{ date }} · 北京时间 07:00 更新</p>
            </div>

            <!-- 统计面板 -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
                <div class="bg-white p-6 rounded-2xl shadow text-center">
                    <div class="text-sm text-gray-500">采集情报</div>
                    <div class="text-4xl font-bold text-blue-600">{{ total }}</div>
                </div>
                <div class="bg-white p-6 rounded-2xl shadow border border-red-200 text-center">
                    <div class="text-sm text-red-600">风险预警</div>
                    <div class="text-4xl font-bold text-red-600">{{ risk_count }}</div>
                </div>
                <div class="bg-white p-6 rounded-2xl shadow border border-blue-200 text-center">
                    <div class="text-sm text-blue-600">政策信号</div>
                    <div class="text-4xl font-bold text-blue-600">{{ policy_count }}</div>
                </div>
                <div class="bg-white p-6 rounded-2xl shadow border border-green-200 text-center">
                    <div class="text-sm text-green-600">正面信号</div>
                    <div class="text-4xl font-bold text-green-600">{{ positive_count }}</div>
                </div>
            </div>

            <!-- 产业动态 -->
            <h2 class="text-2xl font-bold mb-6">📊 分产业动态</h2>
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {% for industry, items in industry_data.items() %}
                <div class="bg-white rounded-2xl shadow p-6 card-hover">
                    <div class="flex justify-between mb-4">
                        <h3 class="font-bold text-lg">{{ industry }}</h3>
                        <span class="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs">{{ items|length }}条</span>
                    </div>
                    {% for item in items[:3] %}
                    <div class="mb-6 last:mb-0 border-b pb-4 last:border-none">
                        <span class="tag-{{ 'positive' if item.impact == '正面' else 'negative' if item.impact == '负面' else 'neutral' }} px-3 py-1 rounded-full text-xs">
                            {{ item.impact }}
                        </span>
                        <p class="mt-3 text-gray-700 text-sm leading-relaxed">{{ item.chinese_summary[:220] }}{% if item.chinese_summary|length > 220 %}...{% endif %}</p>
                        <div class="text-xs text-gray-500 mt-3">
                            重要性：{{ item.importance }} · 
                            {% if item.entities %}{{ item.entities[:2]|join('、') }}{% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% endfor %}
            </div>

            <div class="text-center text-gray-500 text-sm mt-12">
                数据来源：公开RSS媒体 · AI分析由 DeepSeek 提供 · 仅供参考
            </div>
        </div>
    </body>
    </html>
    """
    
    template = Template(html_template)
    html_content = template.render(
        title=REPORT_TITLE,
        date=beijing_time,
        total=total,
        risk_count=risk_count,
        policy_count=policy_count,
        positive_count=positive_count,
        industry_data=industry_data
    )
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML报告生成完成 → index.html (共 {total} 条情报)")

if __name__ == "__main__":
    generate_html_report()
