"""
매일 구글 이미지 크롤링 (최신 데이터) - Supabase 직접 연동
"""

from crawl_google_images import GoogleImageCrawler
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class DailyImageCrawler:
    def __init__(self):
        self.crawler = GoogleImageCrawler()
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
    
    def check_duplicate(self, image_path: str) -> bool:
        """이미지 경로 중복 확인 (최근 7일 내에서만 체크)"""
        try:
            from datetime import datetime, timedelta
            seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/phishing_images",
                headers=self.headers,
                params={
                    'image_path': f'eq.{image_path}',
                    'crawled_at': f'gte.{seven_days_ago}',
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
                f"{self.supabase_url}/rest/v1/phishing_images",
                headers=self.headers,
                json=data,
                timeout=10
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"   삽입 오류: {e}")
            return False
    
    def daily_update(self):
        """매일 구글 이미지 수집 및 Supabase 업로드"""
        print(f"\n{'='*60}")
        print(f"🖼️  구글 이미지 매일 업데이트 ({datetime.now().strftime('%Y-%m-%d')})")
        print(f"{'='*60}\n")
        
        keywords = [
            '스미싱 문자 사례', '스미싱 예시', '스미싱 이미지', 
            '택배 스미싱', '정부지원금 스미싱',
            '카톡 피싱', '가족 사칭 카톡', '자녀 사칭 카톡', '지인 사칭 카톡',
            '보이스피싱 대본', '보이스피싱 문자', '경찰 사칭 문자',
            '피싱 메일 예시', '피싱 사이트 화면', '스캠 메시지',
            '사기 문자 이미지', '부고 문자 사기', '납치 협박 문자',
            '투자 사기 카톡', 'AI 음성 사기'
        ]
        
        # 이미지 수집
        results = self.crawler.run(keywords=keywords, max_images_per_keyword=10)
        
        print(f"\n📊 총 수집: {len(results)}개 이미지\n")
        
        # Supabase 업로드
        success = 0
        duplicate = 0
        error = 0
        
        for idx, item in enumerate(results, 1):
            if idx % 20 == 0:
                print(f"   진행: {idx}/{len(results)} (성공:{success}, 중복:{duplicate}, 실패:{error})")
            
            # local_path를 image_path로 사용
            image_path = item.get('local_path', '')
            if not image_path:
                error += 1
                continue
            
            # DB 중복 체크
            if self.check_duplicate(image_path):
                duplicate += 1
                continue
            
            # 데이터 준비
            record = {
                'source': 'google_images',
                'image_path': image_path,
                'image_url': item.get('image_url', ''),
                'query': item.get('query', ''),
                'language': 'ko',  # 한국어 쿼리로 수집
                'crawled_at': datetime.now().isoformat()
            }
            
            # 삽입
            if self.insert_record(record):
                success += 1
            else:
                error += 1
        
        print(f"\n{'='*60}")
        print(f"✅ 구글 이미지 매일 업데이트 완료")
        print(f"{'='*60}")
        print(f"   성공: {success}건")
        print(f"   중복: {duplicate}건")
        print(f"   실패: {error}건")
        print(f"{'='*60}\n")
        
        return {'success': success, 'duplicate': duplicate, 'error': error}

def main():
    crawler = DailyImageCrawler()
    crawler.daily_update()

if __name__ == "__main__":
    main()
