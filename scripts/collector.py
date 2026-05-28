import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import feedparser
from datetime import datetime, timedelta
import pytz
import json
from config import DAYS_BACK, MAX_NEWS

def fetch_rss_feeds():
    with open('sources.json', 'r', encoding='utf-8') as f:
        sources = json.load(f)['sources']
    
    all_news = []
    cutoff = datetime.now(pytz.UTC) - timedelta(days=DAYS_BACK)
    
    print(f"开始采集，时间窗口：过去 {DAYS_BACK} 天 (截止 {cutoff})")
    
    for source in sources:
        print(f"正在抓取: {source['name']} → {source['url']}")
        try:
            feed = feedparser.parse(source['url'])
            print(f"  → 共发现 {len(feed.entries)} 条条目")
            
            for entry in feed.entries[:25]:
                # 更宽松的日期解析
                pub_date = None
                for date_field in ['published_parsed', 'updated_parsed', 'pubDate_parsed']:
                    if hasattr(entry, date_field) and getattr(entry, date_field):
                        pub_date = getattr(entry, date_field)
                        break
                
                if pub_date:
                    pub_time = datetime(*pub_date[:6], tzinfo=pytz.UTC)
                    if pub_time > cutoff:
                        news_item = {
                            'title': entry.get('title', 'No Title'),
                            'link': entry.get('link', ''),
                            'summary': entry.get('summary', entry.get('description', ''))[:300],
                            'published': pub_time.isoformat(),
                            'source': source['name'],
                            'category': source.get('category', 'general')
                        }
                        all_news.append(news_item)
                else:
                    # 如果没有日期，也保留（作为备选）
                    news_item = {
                        'title': entry.get('title', 'No Title'),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', entry.get('description', ''))[:300],
                        'published': datetime.now(pytz.UTC).isoformat(),
                        'source': source['name'],
                        'category': source.get('category', 'general')
                    }
                    all_news.append(news_item)
                    
        except Exception as e:
            print(f"  → 抓取失败: {e}")
    
    # 去重
    seen = set()
    unique_news = []
    for news in all_news:
        key = (news['title'] + news.get('link', '')).lower()
        if key not in seen and news['title'].strip():
            seen.add(key)
            unique_news.append(news)
    
    print(f"\n采集完成！总共获取 {len(unique_news)} 条唯一新闻")
    return unique_news[:MAX_NEWS]

if __name__ == "__main__":
    os.makedirs('data', exist_ok=True)
    news = fetch_rss_feeds()
    with open('data/raw_news.json', 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
    print("raw_news.json 已保存")
