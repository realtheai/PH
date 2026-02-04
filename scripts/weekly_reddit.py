"""
주 2회 Reddit 크롤링
"""

from crawl_reddit import RedditPhishingCrawler
from datetime import datetime
import json
import os

def weekly_update():
    """주 2회 Reddit 업데이트 (월/목)"""
    print(f"\n{'='*60}")
    print(f"🔴 Reddit 주간 업데이트 ({datetime.now().strftime('%Y-%m-%d')})")
    print(f"{'='*60}")
    
    crawler = RedditPhishingCrawler()
    
    # 전체 서브레딧 (1년치 크롤링과 동일 - 11개)
    subreddits = [
        'Scams', 'phishing', 'cybersecurity', 'EmailScams', 'technology',
        'security', 'privacy', 'korea', 'InformationSecurity', 
        'SocialEngineering', 'DeepfakeScams'
    ]
    
    all_results = []
    
    for subreddit in subreddits:
        results = crawler.search_subreddit(subreddit, limit=50)
        all_results.extend(results)
    
    # 저장
    today = datetime.now().strftime('%Y%m%d')
    os.makedirs('data/raw/weekly', exist_ok=True)
    filename = f'data/raw/weekly/reddit_{today}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Reddit 주간 업데이트 완료: {len(all_results)}건")
    print(f"💾 저장: {filename}")
    
    return all_results

if __name__ == "__main__":
    weekly_update()
