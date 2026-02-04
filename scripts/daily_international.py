"""
매일 해외 뉴스 크롤링 (영어)
"""

from crawl_international_news import InternationalNewsCrawler
from datetime import datetime
import json
import os

def daily_update():
    """매일 해외 뉴스 수집"""
    print(f"\n{'='*60}")
    print(f"🌍 해외 뉴스 매일 업데이트 ({datetime.now().strftime('%Y-%m-%d')})")
    print(f"{'='*60}")
    
    crawler = InternationalNewsCrawler()
    
    # 전체 쿼리 (1년치 크롤링과 동일 - 12개)
    queries = [
        'phishing attack', 'email scam', 'online fraud', 'smishing', 
        'cyber scam', 'voice phishing script', 'deepfake audio scam', 
        'pig butchering scam', 'identity theft cases', 
        'bank impersonation fraud', 'remote access scam',
        'technical support scam'
    ]
    
    # 매일 수집 (각 쿼리당 10개)
    results = crawler.run(queries=queries, max_results_per_query=10)
    
    # 저장
    today = datetime.now().strftime('%Y%m%d')
    os.makedirs('data/raw/daily', exist_ok=True)
    filename = f'data/raw/daily/intl_news_{today}.json'
    
    crawler.save_to_json(results, filename)
    
    print(f"\n✅ 해외 뉴스 매일 업데이트 완료: {len(results)}건")
    print(f"💾 저장: {filename}")
    
    # 통계
    sources = {}
    for r in results:
        source = r.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print(f"\n📊 소스별 통계:")
    for source, count in sources.items():
        print(f"   {source}: {count}건")
    
    return results

if __name__ == "__main__":
    daily_update()
