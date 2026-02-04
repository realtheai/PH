"""
통합 소셜 미디어 크롤러
Reddit + X(Twitter) + Instagram + 해외 뉴스
"""

import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from scripts.crawl_reddit import RedditPhishingCrawler
from scripts.crawl_twitter import TwitterPhishingCrawler
from scripts.crawl_instagram import InstagramPhishingCrawler
from scripts.crawl_international_news import InternationalNewsCrawler


def merge_data(data_list):
    """데이터 병합 및 중복 제거"""
    unique_data = {}
    
    for data in data_list:
        # URL 또는 content를 키로 사용
        key = data.get('url', '') or data.get('content', '')[:100]
        if key and key not in unique_data:
            unique_data[key] = data
    
    return list(unique_data.values())


def main():
    print("\n" + "="*70)
    print("🚀 통합 소셜 미디어 + 해외 뉴스 크롤링")
    print("="*70)
    
    all_data = []
    
    # 1. Reddit
    print("\n" + "="*70)
    print("🔴 1단계: Reddit")
    print("="*70)
    
    reddit_crawler = RedditPhishingCrawler()
    reddit_results = reddit_crawler.run(
        subreddits=['Scams', 'phishing', 'cybersecurity', 'Fraud', 'EmailScams'],
        limit_per_sub=30
    )
    all_data.extend(reddit_results)
    print(f"\n✅ Reddit: {len(reddit_results)}건 수집")
    
    # 2. X (Twitter)
    print("\n" + "="*70)
    print("🐦 2단계: X (Twitter)")
    print("="*70)
    
    twitter_crawler = TwitterPhishingCrawler()
    twitter_results = twitter_crawler.run(
        queries=['phishing alert', 'scam warning', 'smishing'],
        max_results_per_query=20
    )
    all_data.extend(twitter_results)
    print(f"\n✅ Twitter: {len(twitter_results)}건 수집")
    
    # 3. Instagram
    print("\n" + "="*70)
    print("📷 3단계: Instagram")
    print("="*70)
    
    instagram_crawler = InstagramPhishingCrawler()
    instagram_results = instagram_crawler.run(
        hashtags=['phishing', 'scam', 'cybersecurity'],
        max_results_per_tag=15
    )
    all_data.extend(instagram_results)
    print(f"\n✅ Instagram: {len(instagram_results)}건 수집")
    
    # 4. 해외 뉴스
    print("\n" + "="*70)
    print("🌍 4단계: 해외 뉴스")
    print("="*70)
    
    news_crawler = InternationalNewsCrawler()
    news_results = news_crawler.run(
        queries=['phishing attack', 'email scam', 'online fraud']
    )
    all_data.extend(news_results)
    print(f"\n✅ 해외 뉴스: {len(news_results)}건 수집")
    
    # 5. 데이터 병합 및 중복 제거
    print("\n" + "="*70)
    print("🔄 5단계: 데이터 병합 및 중복 제거")
    print("="*70)
    
    merged_data = merge_data(all_data)
    
    # 6. 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'data/raw/social_all_{timestamp}.json'
    
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    # 7. 통계 출력
    print("\n" + "="*70)
    print("📊 최종 결과")
    print("="*70)
    print(f"\n총 수집: {len(all_data)}건")
    print(f"중복 제거: {len(merged_data)}건")
    print(f"\n💾 저장 위치: {output_file}")
    
    # 출처별 통계
    source_stats = {}
    for item in merged_data:
        source = item.get('source', 'unknown')
        source_stats[source] = source_stats.get(source, 0) + 1
    
    print(f"\n📈 출처별 통계:")
    for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {source}: {count}건")
    
    # 추출된 키워드 통계
    extracted_keywords = {}
    for item in merged_data:
        for kw in item.get('extracted_keywords', []):
            extracted_keywords[kw] = extracted_keywords.get(kw, 0) + 1
    
    print(f"\n🎯 추출된 키워드 (상위 10개):")
    for kw, count in sorted(extracted_keywords.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   - {kw}: {count}건")
    
    print("\n" + "="*70)
    print("✅ 크롤링 완료!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
