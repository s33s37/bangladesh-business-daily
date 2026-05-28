from collector import fetch_rss_feeds
from analyzer import analyze_news
from generator import generate_html_report
import json

def main():
    print("=== 孟加拉商业情报日报 开始生成 ===")
    
    # 1. 采集新闻
    news = fetch_rss_feeds()
    with open('data/raw_news.json', 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    
    # 2. AI 分析
    analyzed = analyze_news(news)
    with open('data/analyzed_news.json', 'w', encoding='utf-8') as f:
        json.dump(analyzed, f, ensure_ascii=False, indent=2)
    
    # 3. 生成网页
    generate_html_report(analyzed)
    
    print("=== 日报生成完成！ ===")

if __name__ == "__main__":
    main()
