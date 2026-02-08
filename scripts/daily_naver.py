"""
매일 네이버 API 크롤링 (최신 데이터) - Supabase 직접 연동
"""

from crawl_naver_api import NaverAPINewsCrawler
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class DailyNaverCrawler:
    def __init__(self):
        self.crawler = NaverAPINewsCrawler()
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
    
    def check_duplicate(self, url: str) -> bool:
        """URL 중복 확인 (최근 30일 내에서 체크 - 개선됨)"""
        try:
            from datetime import datetime, timedelta
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/phishing_news",
                headers=self.headers,
                params={
                    'url': f'eq.{url}',
                    'crawled_at': f'gte.{thirty_days_ago}',
                    'select': 'id'
                },
                timeout=5
            )
            return len(response.json()) > 0
        except:
            return False
    
    def insert_record(self, data: dict) -> bool:
        """단일 레코드 삽입"""
        try:
            response = requests.post(
                f"{self.supabase_url}/rest/v1/phishing_news",
                headers=self.headers,
                json=data,
                timeout=10
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"   삽입 오류: {e}")
            return False
    
    def daily_update(self):
        """매일 네이버 최신 뉴스 수집 및 Supabase 업로드 (전날 24시간만)"""
        print(f"\n{'='*60}")
        print(f"📰 네이버 매일 업데이트 ({datetime.now().strftime('%Y-%m-%d')})")
        print(f"{'='*60}\n")
        
        # 날짜 범위 설정 (전날 24시간)
        from datetime import timedelta
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        start_date = yesterday.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        print(f"📅 수집 기간: {start_date} ~ {end_date} (전날 24시간)\n")
        
        # 전체 키워드
        keywords = [
            '피싱', '스미싱', '보이스피싱', '메신저피싱',
            '기관 사칭 피싱', '경찰 사칭', '검찰 사칭', '금융감독원 사칭',
            '은행 사칭 문자', '카드사 사칭', '택배 사칭', '우체국 사칭',
            '가족 사칭 문자', '자녀 사칭 카톡', '지인 사칭 피싱',
            '납치 협박 문자', '부고 문자 사기', '돌잔치 청첩장 스미싱',
            '교통범칙금 문자', '과태료 납부 사기',
            '정부 지원금 사기', '재난지원금 피싱', '환급금 사기',
            '대출 빙자 사기', '투자 사기 문자',
            '딥보이스 피싱', 'AI 음성 사기', '메타버스 피싱', '가상자산 피싱'
        ]
        
        all_results = []
        
        for idx, keyword in enumerate(keywords, 1):
            print(f"[{idx}/{len(keywords)}] '{keyword}' 검색 중...")
            results = self.crawler.search_news(
                keyword, 
                display=100, 
                start=1,
                start_date=start_date,  # 날짜 필터 추가
                end_date=end_date        # 날짜 필터 추가
            )
            all_results.extend(results)
            print(f"   수집: {len(results)}건")
        
        # 로컬 중복 제거
        unique_results = {}
        for r in all_results:
            url = r['url']
            if url not in unique_results:
                unique_results[url] = r
        
        final_results = list(unique_results.values())
        print(f"\n📊 총 수집: {len(final_results)}건 (로컬 중복 제거)\n")
        
        # Supabase 업로드
        success = 0
        duplicate = 0
        error = 0
        
        for idx, item in enumerate(final_results, 1):
            if idx % 20 == 0:
                print(f"   진행: {idx}/{len(final_results)} (성공:{success}, 중복:{duplicate}, 실패:{error})")
            
            # DB 중복 체크
            if self.check_duplicate(item['url']):
                duplicate += 1
                continue
            
            # 데이터 준비
            record = {
                'source': 'naver',
                'title': item['title'],
                'content': item.get('content', ''),
                'url': item['url'],
                'original_language': 'ko',
                'content_length': len(item.get('content', '')),
                'published_at': item.get('date'),
                'crawled_at': datetime.now().isoformat()
            }
            
            # 삽입
            if self.insert_record(record):
                success += 1
            else:
                error += 1
        
        print(f"\n{'='*60}")
        print(f"✅ 네이버 매일 업데이트 완료")
        print(f"{'='*60}")
        print(f"   성공: {success}건")
        print(f"   중복: {duplicate}건")
        print(f"   실패: {error}건")
        print(f"{'='*60}\n")
        
        return {'success': success, 'duplicate': duplicate, 'error': error}

def main():
    crawler = DailyNaverCrawler()
    crawler.daily_update()

if __name__ == "__main__":
    main()
