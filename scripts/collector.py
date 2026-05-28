import feedparser
import requests
from datetime import datetime, timedelta
import pytz
import json
from config import DAYS_BACK, MAX_NEWS

def fetch_rss_feeds():
    with open('sources.json', 'r', encoding='utf-8') as f:
        sources = json.load(f)['sources']
    
    all_news = []
    cutoff = datetime.now(pytz.UTC) - timedelta(days=DAYS_BACK)
    
    for source in sources:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:20]:
                pub_date = entry.get('published_parsed') or entry.get('updated_parsed')
                if pub_date:
                    pub_time = datetime(*pub_date[:6], tzinfo=pytz.UTC)
                    if pub_time > cutoff:
                        all_news.append({
                            'title': entry.title,
                            'link': entry.link,
                            'summary': entry.get('summary', ''),
                            'published': pub_time.isoformat(),
                            'source': source['name'],
                            'category': source.get('category', 'general')
                        })
        except Exception as e:
            print(f"Error fetching {source['name']}: {e}")
    
    # 去重
    seen = set()
    unique_news = []
    for news in all_news:
        key = news['title'] + news['link']
        if key not in seen:
            seen.add(key)
            unique_news.append(news)
    
    print(f"采集到 {len(unique_news)} 条新闻")
    return unique_news[:MAX_NEWS]

if __name__ == "__main__":
    news = fetch_rss_feeds()
    with open('data/raw_news.json', 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
