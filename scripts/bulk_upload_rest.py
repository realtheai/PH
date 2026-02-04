"""
1년치 데이터 대량 업로드 (REST API 직접 사용)
"""
import os
import json
import requests
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

class SimpleBulkUploader:
    def __init__(self):
        self.base_url = f"{SUPABASE_URL}/rest/v1"
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
    def classify_content(self, title: str, content: str) -> str:
        """간단한 키워드 기반 분류"""
        text = title + " " + content
        if any(kw in text for kw in ['피해', '사례', '적발', '검거', '당해', '속아']):
            return 'REAL_CASE'
        elif any(kw in text for kw in ['예방', '캠페인', '주의', '대응', '경보']):
            return 'NEWS'
        else:
            return 'NEWS'
    
    def check_duplicate(self, url: str) -> bool:
        """URL 중복 확인"""
        try:
            response = requests.get(
                f"{self.base_url}/phishing_news",
                headers=self.headers,
                params={'url': f'eq.{url}', 'select': 'id'},
                timeout=5
            )
            return len(response.json()) > 0
        except:
            return False
    
    def insert_record(self, data: Dict) -> bool:
        """단일 레코드 삽입"""
        try:
            response = requests.post(
                f"{self.base_url}/phishing_news",
                headers=self.headers,
                json=data,
                timeout=10
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"   삽입 오류: {e}")
            return False
    
    def process_and_upload_naver(self, json_file: str) -> Dict:
        """네이버 데이터 처리 및 업로드"""
        print(f"\n📰 네이버 데이터: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"   전체: {len(data)}건")
        
        success = 0
        duplicate = 0
        error = 0
        
        for idx, item in enumerate(data, 1):
            if idx % 50 == 0:
                print(f"   진행: {idx}/{len(data)} (성공:{success}, 중복:{duplicate}, 실패:{error})")
            
            # 중복 체크
            if self.check_duplicate(item['url']):
                duplicate += 1
                continue
            
            # 데이터 준비
            record = {
                'source': 'naver',
                'title': item['title'],
                'content': item.get('content', ''),
                'url': item['url'],
                'category': self.classify_content(item['title'], item.get('content', '')),
                'original_language': 'ko',
                'content_length': len(item.get('content', '')),
                'published_at': item.get('date'),
                'crawled_at': item['crawled_at']
            }
            
            # 삽입
            if self.insert_record(record):
                success += 1
            else:
                error += 1
        
        print(f"   완료: 성공 {success}, 중복 {duplicate}, 실패 {error}")
        return {'success': success, 'duplicate': duplicate, 'error': error}
    
    def process_and_upload_google(self, json_file: str) -> Dict:
        """구글 뉴스 데이터 처리 및 업로드"""
        print(f"\n🌐 구글 뉴스: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"   전체: {len(data)}건")
        
        success = 0
        duplicate = 0
        error = 0
        
        for idx, item in enumerate(data, 1):
            if idx % 50 == 0:
                print(f"   진행: {idx}/{len(data)} (성공:{success}, 중복:{duplicate}, 실패:{error})")
            
            if self.check_duplicate(item['url']):
                duplicate += 1
                continue
            
            record = {
                'source': 'google',
                'title': item['title'],
                'content': item.get('content', ''),
                'url': item['url'],
                'category': self.classify_content(item['title'], item.get('content', '')),
                'original_language': 'ko',
                'content_length': len(item.get('content', '')),
                'published_at': item.get('published_at'),
                'crawled_at': item['crawled_at']
            }
            
            if self.insert_record(record):
                success += 1
            else:
                error += 1
        
        print(f"   완료: 성공 {success}, 중복 {duplicate}, 실패 {error}")
        return {'success': success, 'duplicate': duplicate, 'error': error}
    
    def process_and_upload_reddit(self, json_file: str) -> Dict:
        """Reddit 데이터 처리 및 업로드"""
        print(f"\n🔴 Reddit: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"   전체: {len(data)}건")
        
        success = 0
        duplicate = 0
        error = 0
        
        for idx, item in enumerate(data, 1):
            if idx % 50 == 0:
                print(f"   진행: {idx}/{len(data)} (성공:{success}, 중복:{duplicate}, 실패:{error})")
            
            if self.check_duplicate(item['url']):
                duplicate += 1
                continue
            
            record = {
                'source': 'reddit',
                'title': item['title'],
                'content': item.get('content', ''),
                'url': item['url'],
                'category': 'NEWS',
                'original_language': 'en',
                'content_length': len(item.get('content', '')),
                'published_at': datetime.fromtimestamp(item['created_utc']).isoformat() if 'created_utc' in item else None,
                'crawled_at': item['crawled_at']
            }
            
            if self.insert_record(record):
                success += 1
            else:
                error += 1
        
        print(f"   완료: 성공 {success}, 중복 {duplicate}, 실패 {error}")
        return {'success': success, 'duplicate': duplicate, 'error': error}

def main():
    print("="*60)
    print("📦 1년치 데이터 대량 업로드 (REST API)")
    print("="*60)
    
    uploader = SimpleBulkUploader()
    
    total_stats = {'success': 0, 'duplicate': 0, 'error': 0}
    
    # 1. 네이버
    print("\n" + "="*60)
    print("1/3: 네이버 뉴스")
    print("="*60)
    naver_stats = uploader.process_and_upload_naver(
        'data/raw/naver_api_2025-02-01_to_2026-01-31_fixed.json'
    )
    for key in total_stats:
        total_stats[key] += naver_stats[key]
    
    # 2. 구글
    print("\n" + "="*60)
    print("2/3: 구글 뉴스")
    print("="*60)
    google_stats = uploader.process_and_upload_google(
        'data/raw/google_news_2025-02-01_to_2026-01-31.json'
    )
    for key in total_stats:
        total_stats[key] += google_stats[key]
    
    # 3. Reddit
    print("\n" + "="*60)
    print("3/3: Reddit")
    print("="*60)
    reddit_stats = uploader.process_and_upload_reddit(
        'data/raw/reddit_2025-02-01_to_2026-01-31.json'
    )
    for key in total_stats:
        total_stats[key] += reddit_stats[key]
    
    # 최종 결과
    print("\n" + "="*60)
    print("📊 최종 업로드 결과")
    print("="*60)
    print(f"✅ 성공: {total_stats['success']:,}건")
    print(f"⚠️  중복: {total_stats['duplicate']:,}건")
    print(f"❌ 실패: {total_stats['error']:,}건")
    print("="*60)

if __name__ == "__main__":
    main()
