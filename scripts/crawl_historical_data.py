"""
1년치 과거 데이터 크롤링 스크립트
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import time
import json

sys.path.append(str(Path(__file__).parent.parent))

from scripts.crawl_naver_api import NaverAPINewsCrawler
from scripts.crawl_google_news import GoogleNewsCrawler
from scripts.crawl_reddit import RedditPhishingCrawler
from scripts.crawl_international_news import InternationalNewsCrawler


def crawl_historical_naver(months: int = 12):
    """네이버 뉴스 과거 데이터 수집"""
    print(f"\n{'='*60}")
    print(f"📰 네이버 뉴스 - 과거 {months}개월 크롤링")
    print(f"{'='*60}")
    
    crawler = NaverAPINewsCrawler()
    
    keywords = [
        '피싱 주의보',
        '스미싱 사례',
        '보이스피싱 피해',
        '금융사기',
        '메신저피싱',
        '택배 스미싱',
        '카드론 피싱'
    ]
    
    all_results = []
    
    # 월별로 크롤링
    for month_offset in range(months):
        target_date = datetime.now() - timedelta(days=30 * month_offset)
        year_month = target_date.strftime('%Y-%m')
        
        print(f"\n📅 {year_month} 데이터 수집 중...")
        
        for keyword in keywords:
            results = crawler.search_news(
                query=f"{keyword} {year_month}",
                display=100
            )
            all_results.extend(results)
            time.sleep(0.5)
    
    # 중복 제거
    unique_results = {}
    for result in all_results:
        url = result['url']
        if url not in unique_results:
            unique_results[url] = result
    
    final_results = list(unique_results.values())
    
    print(f"\n✅ 네이버: {len(final_results)}건 수집")
    return final_results


def crawl_historical_reddit(months: int = 12):
    """Reddit 과거 데이터 수집"""
    print(f"\n{'='*60}")
    print(f"🔴 Reddit - 과거 {months}개월 크롤링")
    print(f"{'='*60}")
    
    crawler = RedditPhishingCrawler()
    
    # Reddit은 시간 필터링 지원
    subreddits = [
        'Scams',
        'phishing',
        'cybersecurity',
        'EmailScams',
        'privacy'
    ]
    
    all_results = []
    
    for subreddit in subreddits:
        # Top posts from past year
        results = crawler.search_subreddit(
            subreddit=subreddit,
            limit=100
        )
        all_results.extend(results)
        time.sleep(3)
    
    print(f"\n✅ Reddit: {len(all_results)}건 수집")
    return all_results


def crawl_historical_google(months: int = 12):
    """구글 뉴스 과거 데이터 수집"""
    print(f"\n{'='*60}")
    print(f"🌐 구글 뉴스 - 과거 {months}개월 크롤링")
    print(f"{'='*60}")
    
    crawler = GoogleNewsCrawler()
    
    keywords_kr = [
        '피싱 사례',
        '스미싱 주의',
        '보이스피싱',
        '금융사기'
    ]
    
    all_results = []
    
    for keyword in keywords_kr:
        results = crawler.search_news(keyword, max_results=100)
        all_results.extend(results)
        time.sleep(3)
    
    print(f"\n✅ 구글: {len(all_results)}건 수집")
    return all_results


def main():
    """1년치 전체 크롤링"""
    print(f"\n{'='*70}")
    print(f"🚀 1년치 과거 데이터 크롤링 시작")
    print(f"{'='*70}")
    
    months = 12
    all_data = []
    
    # 1. 네이버 (가장 많은 데이터)
    naver_results = crawl_historical_naver(months=months)
    all_data.extend(naver_results)
    
    # 2. Reddit
    reddit_results = crawl_historical_reddit(months=months)
    all_data.extend(reddit_results)
    
    # 3. 구글 뉴스
    google_results = crawl_historical_google(months=months)
    all_data.extend(google_results)
    
    # 4. 중복 제거
    unique_data = {}
    for item in all_data:
        key = item.get('url', '') or item.get('content', '')[:100]
        if key and key not in unique_data:
            unique_data[key] = item
    
    final_data = list(unique_data.values())
    
    # 5. 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'data/raw/historical_1year_{timestamp}.json'
    
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    # 6. 통계
    print(f"\n{'='*70}")
    print(f"📊 최종 결과")
    print(f"{'='*70}")
    print(f"\n총 수집: {len(all_data)}건")
    print(f"중복 제거: {len(final_data)}건")
    print(f"\n💾 저장 위치: {output_file}")
    
    # 출처별 통계
    source_stats = {}
    for item in final_data:
        source = item.get('source', 'unknown')
        source_stats[source] = source_stats.get(source, 0) + 1
    
    print(f"\n📈 출처별 통계:")
    for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {source}: {count}건")
    
    print(f"\n{'='*70}")
    print(f"✅ 1년치 크롤링 완료!")
    print(f"{'='*70}\n")
    
    return final_data


if __name__ == "__main__":
    main()
