"""
매일 Reddit 크롤링 - Supabase 직접 연동
"""

from crawl_reddit import RedditPhishingCrawler
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class DailyRedditCrawler:
    def __init__(self):
        self.crawler = RedditPhishingCrawler()
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
    
    def check_duplicate(self, url: str) -> bool:
        """URL 중복 확인 (최근 7일 내에서만 체크)"""
        try:
            from datetime import datetime, timedelta
            seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
            
            response = requests.get(
                f"{self.supabase_url}/rest/v1/phishing_news",
                headers=self.headers,
                params={
                    'url': f'eq.{url}',
                    'crawled_at': f'gte.{seven_days_ago}',
                    'select': 'id'
                },
                timeout=5
            )
            return len(response.json()) > 0
        except:
            return False
    
    def insert_record(self, data: dict) -> tuple:
        """단일 레코드 삽입
        
        Returns:
            (success: bool, is_duplicate: bool)
        """
        try:
            response = requests.post(
                f"{self.supabase_url}/rest/v1/phishing_news",
                headers=self.headers,
                json=data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return (True, False)  # 성공
            elif response.status_code == 409:
                # HTTP 409 = 중복 (unique constraint 위반)
                return (False, True)  # 중복
            else:
                print(f"   ⚠️  삽입 실패 (HTTP {response.status_code}): {response.text[:200]}")
                return (False, False)  # 실패
                
        except Exception as e:
            print(f"   ❌ 삽입 오류: {e}")
            return (False, False)  # 실패
    
    def daily_update(self):
        """매일 Reddit 수집 및 Supabase 업로드"""
        print(f"\n{'='*60}")
        print(f"🔴 Reddit 매일 업데이트 ({datetime.now().strftime('%Y-%m-%d')})")
        print(f"{'='*60}\n")
        
        subreddits = [
            'Scams', 'phishing', 'cybersecurity', 'EmailScams', 'technology',
            'security', 'privacy', 'korea', 'InformationSecurity', 
            'SocialEngineering', 'DeepfakeScams'
        ]
        
        # Reddit 수집
        results = self.crawler.run(subreddits=subreddits, limit_per_sub=20)
        
        print(f"\n📊 총 수집: {len(results)}개 포스트\n")
        
        # Supabase 업로드
        success_count = 0
        duplicate = 0
        error = 0
        
        for idx, item in enumerate(results, 1):
            if idx % 20 == 0:
                print(f"   진행: {idx}/{len(results)} (성공:{success_count}, 중복:{duplicate}, 실패:{error})")
            
            url = item.get('url', '')
            if not url:
                error += 1
                continue
            
            # DB 중복 체크
            if self.check_duplicate(url):
                duplicate += 1
                continue
            
            # 데이터 준비
            # Unix timestamp → ISO 8601 변환
            created_utc = item.get('created_utc')
            published_at = None
            if created_utc:
                try:
                    published_at = datetime.fromtimestamp(float(created_utc)).isoformat()
                except:
                    published_at = None
            
            record = {
                'source': 'reddit',
                'title': item.get('title', ''),
                'content': item.get('selftext', ''),
                'url': url,
                'original_language': 'en',  # Reddit은 대부분 영어
                'content_length': len(item.get('selftext', '')),
                'published_at': published_at,
                'crawled_at': datetime.now().isoformat()
            }
            
            # 삽입
            success, is_duplicate = self.insert_record(record)
            if success:
                success_count += 1
            elif is_duplicate:
                duplicate += 1
            else:
                error += 1
        
        print(f"\n{'='*60}")
        print(f"✅ Reddit 매일 업데이트 완료")
        print(f"{'='*60}")
        print(f"   ✅ 성공: {success_count}건 (새로 추가)")
        print(f"   ℹ️  중복: {duplicate}건 (이미 존재)")
        print(f"   ❌ 실패: {error}건")
        print(f"{'='*60}\n")
        
        return {'success': success_count, 'duplicate': duplicate, 'error': error}

def main():
    crawler = DailyRedditCrawler()
    crawler.daily_update()

if __name__ == "__main__":
    main()
