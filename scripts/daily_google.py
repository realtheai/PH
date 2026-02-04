"""
매일 구글 뉴스 크롤링 (최신 데이터)
"""

from crawl_google_news import GoogleNewsCrawler
from datetime import datetime
import json
import os

# Note: GoogleNewsCrawler에 이미 newspaper3k 본문 추출 기능이 포함되어 있음

def daily_update():
    """매일 구글 최신 뉴스 수집"""
    print(f"\n{'='*60}")
    print(f"🌐 구글 매일 업데이트 ({datetime.now().strftime('%Y-%m-%d')})")
    print(f"{'='*60}")
    
    crawler = GoogleNewsCrawler()
    
    # 전체 키워드 (1년치 크롤링과 동일 - 28개)
    keywords = [
        # 기본 피싱/스미싱
        '피싱', '스미싱', '보이스피싱', '메신저피싱',
        
        # 사칭 유형
        '기관 사칭 피싱', '경찰 사칭', '검찰 사칭', '금융감독원 사칭',
        '은행 사칭 문자', '카드사 사칭', '택배 사칭', '우체국 사칭',
        
        # 구체적 수법
        '가족 사칭 문자', '자녀 사칭 카톡', '지인 사칭 피싱',
        '납치 협박 문자', '부고 문자 사기', '돌잔치 청첩장 스미싱',
        '교통범칙금 문자', '과태료 납부 사기',
        
        # 금전 관련
        '정부 지원금 사기', '재난지원금 피싱', '환급금 사기',
        '대출 빙자 사기', '투자 사기 문자',
        
        # 최신 트렌드
        '딥보이스 피싱', 'AI 음성 사기', '메타버스 피싱',
        '가상자산 피싱'
    ]
    
    all_results = []
    
    for keyword in keywords:
        results = crawler.search_news(keyword, max_results=50)
        all_results.extend(results)
    
    # 중복 제거
    unique_results = {}
    for r in all_results:
        url = r.get('url', '')
        if url and url not in unique_results:
            unique_results[url] = r
    
    final_results = list(unique_results.values())
    
    # 저장
    today = datetime.now().strftime('%Y%m%d')
    os.makedirs('data/raw/daily', exist_ok=True)
    filename = f'data/raw/daily/google_{today}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 구글 매일 업데이트 완료: {len(final_results)}건")
    print(f"💾 저장: {filename}")
    
    return final_results

if __name__ == "__main__":
    daily_update()
