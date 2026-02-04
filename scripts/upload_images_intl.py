"""
이미지 & 해외 뉴스 업로드
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

class ImageUploader:
    def __init__(self):
        self.base_url = f"{SUPABASE_URL}/rest/v1"
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
    
    def upload_images(self, json_file: str):
        """구글 이미지 업로드"""
        print(f"\n🖼️  구글 이미지 업로드: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"   전체: {len(data)}건")
        
        success = 0
        duplicate = 0
        error = 0
        
        for idx, item in enumerate(data, 1):
            if idx % 50 == 0:
                print(f"   진행: {idx}/{len(data)} (성공:{success}, 중복:{duplicate}, 실패:{error})")
            
            # 이미지 URL 중복 체크 (간단히 스킵)
            record = {
                'query': item.get('query', ''),
                'image_url': item.get('image_url', ''),
                'local_path': item.get('local_path', ''),
                'language': 'unknown',  # OCR 전에는 알 수 없음
                'crawled_at': item.get('crawled_at')
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/phishing_images",
                    headers=self.headers,
                    json=record,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    success += 1
                elif response.status_code == 409:
                    duplicate += 1
                else:
                    error += 1
                    if error <= 3:
                        print(f"\n   오류 {error}: {response.text[:100]}")
            except Exception as e:
                error += 1
                if error <= 3:
                    print(f"\n   예외 {error}: {e}")
        
        print(f"   완료: 성공 {success}, 중복 {duplicate}, 실패 {error}")
        return {'success': success, 'duplicate': duplicate, 'error': error}
    
    def upload_international_news(self, json_file: str):
        """해외 뉴스 업로드"""
        print(f"\n🌍 해외 뉴스 업로드: {json_file}")
        
        if not os.path.exists(json_file):
            print(f"   ⚠️  파일 없음: {json_file}")
            return {'success': 0, 'duplicate': 0, 'error': 0}
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"   전체: {len(data)}건")
        
        success = 0
        duplicate = 0
        error = 0
        
        for idx, item in enumerate(data, 1):
            if idx % 50 == 0:
                print(f"   진행: {idx}/{len(data)} (성공:{success}, 중복:{duplicate}, 실패:{error})")
            
            record = {
                'source': 'international',
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'url': item.get('url', item.get('link', '')),
                'category': 'NEWS',
                'original_language': 'en',
                'content_length': len(item.get('content', '')),
                'published_at': item.get('published_at', item.get('date')),
                'crawled_at': item.get('crawled_at')
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/phishing_news",
                    headers=self.headers,
                    json=record,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    success += 1
                elif response.status_code == 409:
                    duplicate += 1
                else:
                    error += 1
            except Exception as e:
                error += 1
        
        print(f"   완료: 성공 {success}, 중복 {duplicate}, 실패 {error}")
        return {'success': success, 'duplicate': duplicate, 'error': error}

def main():
    print("="*60)
    print("📦 이미지 & 해외 데이터 업로드")
    print("="*60)
    
    uploader = ImageUploader()
    
    # 1. 구글 이미지
    print("\n" + "="*60)
    print("1/2: 구글 이미지")
    print("="*60)
    
    # 1년치 이미지 파일 찾기
    image_file = 'data/raw/google_images_20260131_145232.json'
    if os.path.exists(image_file):
        image_stats = uploader.upload_images(image_file)
    else:
        print(f"   ⚠️  이미지 파일 없음: {image_file}")
        image_stats = {'success': 0, 'duplicate': 0, 'error': 0}
    
    # 2. 해외 뉴스
    print("\n" + "="*60)
    print("2/2: 해외 뉴스")
    print("="*60)
    
    intl_file = 'data/raw/intl_news_2025-02-01_to_2026-01-31.json'
    if os.path.exists(intl_file):
        intl_stats = uploader.upload_international_news(intl_file)
    else:
        # daily 폴더 확인
        intl_file_daily = 'data/raw/daily/intl_news_20260131_145026.json'
        if os.path.exists(intl_file_daily):
            intl_stats = uploader.upload_international_news(intl_file_daily)
        else:
            print(f"   ⚠️  해외 뉴스 파일 없음")
            intl_stats = {'success': 0, 'duplicate': 0, 'error': 0}
    
    # 최종 결과
    print("\n" + "="*60)
    print("📊 업로드 결과")
    print("="*60)
    print(f"🖼️  이미지: 성공 {image_stats['success']}, 중복 {image_stats['duplicate']}, 실패 {image_stats['error']}")
    print(f"🌍 해외 뉴스: 성공 {intl_stats['success']}, 중복 {intl_stats['duplicate']}, 실패 {intl_stats['error']}")
    print("="*60)

if __name__ == "__main__":
    main()
