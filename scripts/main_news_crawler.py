"""
통합 뉴스 크롤러 - 네이버 + 구글
"""

import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from scripts.crawl_naver_news import NaverNewsCrawler
from scripts.crawl_google_news import GoogleNewsCrawler


def merge_data(data_list):
    """데이터 병합 및 중복 제거"""
    unique_data = {}
    
    for data in data_list:
        url = data.get('url', '')
        if url and url not in unique_data:
            unique_data[url] = data
    
    return list(unique_data.values())


def main():
    print("\n" + "="*70)
    print("🚀 통합 뉴스 크롤링 시작 (네이버 + 구글)")
    print("="*70)
    
    # 피싱 관련 키워드 (한국어)
    keywords_kr = [
        '피싱 주의보',
        '스미싱 사례',
        '보이스피싱 피해',
        '금융사기 수법',
        '메신저피싱',
        '계좌이체 사기',
        '개인정보 탈취',
        '공공기관 사칭',
        '택배 스미싱',
        '카드론 피싱',
        '환급금 사기',
        '금융감독원 피싱'
    ]
    
    all_data = []
    
    # 1. 네이버 뉴스 크롤링
    print("\n" + "="*70)
    print("📰 1단계: 네이버 뉴스")
    print("="*70)
    
    naver_crawler = NaverNewsCrawler()
    naver_results = naver_crawler.run(
        keywords=keywords_kr,
        max_pages_per_keyword=5  # 키워드당 5페이지 (약 50건)
    )
    all_data.extend(naver_results)
    
    print(f"\n✅ 네이버: {len(naver_results)}건 수집")
    
    # 2. 구글 뉴스 크롤링
    print("\n" + "="*70)
    print("🌐 2단계: 구글 뉴스")
    print("="*70)
    
    google_crawler = GoogleNewsCrawler()
    google_results = google_crawler.run(
        keywords=keywords_kr,
        max_results_per_keyword=30  # 키워드당 최대 30건
    )
    all_data.extend(google_results)
    
    print(f"\n✅ 구글: {len(google_results)}건 수집")
    
    # 3. 데이터 병합 및 중복 제거
    print("\n" + "="*70)
    print("🔄 3단계: 데이터 병합 및 중복 제거")
    print("="*70)
    
    merged_data = merge_data(all_data)
    
    # 4. 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'data/raw/news_all_{timestamp}.json'
    
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    # 5. 통계 출력
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
    for source, count in source_stats.items():
        print(f"   - {source}: {count}건")
    
    # 키워드별 통계
    keyword_stats = {}
    for item in merged_data:
        keyword = item.get('keyword', 'unknown')
        keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1
    
    print(f"\n🔑 키워드별 통계 (상위 10개):")
    for keyword, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   - {keyword}: {count}건")
    
    # 추출된 피싱 키워드 통계
    extracted_keywords = {}
    for item in merged_data:
        for kw in item.get('extracted_keywords', []):
            extracted_keywords[kw] = extracted_keywords.get(kw, 0) + 1
    
    print(f"\n🎯 추출된 피싱 키워드 (상위 15개):")
    for kw, count in sorted(extracted_keywords.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"   - {kw}: {count}건")
    
    print("\n" + "="*70)
    print("✅ 크롤링 완료!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
