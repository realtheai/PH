"""
매일 구글 이미지 크롤링 (최신 데이터)
"""

from crawl_google_images import GoogleImageCrawler
from datetime import datetime
import json
import os

def daily_update():
    """매일 구글 이미지 수집"""
    print(f"\n{'='*60}")
    print(f"🖼️  구글 이미지 매일 업데이트 ({datetime.now().strftime('%Y-%m-%d')})")
    print(f"{'='*60}")
    
    crawler = GoogleImageCrawler()
    
    # 전체 키워드 (1년치 크롤링과 동일 - 20개)
    keywords = [
        # 스미싱 관련
        '스미싱 문자 사례', '스미싱 예시', '스미싱 이미지', 
        '택배 스미싱', '정부지원금 스미싱',
        
        # 카카오톡 피싱
        '카톡 피싱', '가족 사칭 카톡', '자녀 사칭 카톡', '지인 사칭 카톡',
        
        # 보이스피싱 스크립트
        '보이스피싱 대본', '보이스피싱 문자', '경찰 사칭 문자',
        
        # 기타
        '피싱 메일 예시', '피싱 사이트 화면', '스캠 메시지',
        '사기 문자 이미지', '부고 문자 사기', '납치 협박 문자',
        '투자 사기 카톡', 'AI 음성 사기'
    ]
    
    # 최신 이미지 수집 (각 키워드당 10개만)
    results = crawler.run(keywords=keywords, max_images_per_keyword=10)
    
    # 저장
    today = datetime.now().strftime('%Y%m%d')
    os.makedirs('data/raw/daily', exist_ok=True)
    
    # 메타데이터 저장
    metadata_file = f'data/raw/daily/google_images_{today}.json'
    crawler.save_metadata(results, metadata_file)
    
    print(f"\n✅ 구글 이미지 매일 업데이트 완료: {len(results)}개")
    print(f"💾 메타데이터: {metadata_file}")
    print(f"💾 이미지 저장: data/images/phishing/")
    
    # 통계
    unique_keywords = set(r['query'] for r in results)
    print(f"\n📊 통계:")
    print(f"   키워드: {len(unique_keywords)}개")
    print(f"   이미지: {len(results)}개")
    
    return results

if __name__ == "__main__":
    daily_update()
