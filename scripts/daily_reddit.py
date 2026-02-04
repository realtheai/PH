"""
매일 Reddit 크롤링
"""

from crawl_reddit import RedditPhishingCrawler
from datetime import datetime
import json
import os

def daily_update():
    """매일 Reddit 업데이트"""
    print(f"\n{'='*60}")
    print(f"🔴 Reddit 매일 업데이트 ({datetime.now().strftime('%Y-%m-%d')})")
    print(f"{'='*60}")
    
    crawler = RedditPhishingCrawler()
    
    # 전체 서브레딧 (1년치 크롤링과 동일 - 11개)
    subreddits = [
        'Scams', 'phishing', 'cybersecurity', 'EmailScams', 'technology',
        'security', 'privacy', 'korea', 'InformationSecurity', 
        'SocialEngineering', 'DeepfakeScams'
    ]
    
    # 매일 수집 (각 서브레딧당 20개)
    results = crawler.run(subreddits=subreddits, limit_per_sub=20)
    
    # 저장
    today = datetime.now().strftime('%Y%m%d')
    os.makedirs('data/raw/daily', exist_ok=True)
    filename = f'data/raw/daily/reddit_{today}.json'
    
    crawler.save_to_json(results, filename)
    
    print(f"\n✅ Reddit 매일 업데이트 완료: {len(results)}건")
    print(f"💾 저장: {filename}")
    
    # 통계
    subreddit_stats = {}
    for r in results:
        sub = r.get('subreddit', 'unknown')
        subreddit_stats[sub] = subreddit_stats.get(sub, 0) + 1
    
    print(f"\n📊 서브레딧별 통계:")
    for sub, count in sorted(subreddit_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   r/{sub}: {count}건")
    
    return results

if __name__ == "__main__":
    daily_update()
