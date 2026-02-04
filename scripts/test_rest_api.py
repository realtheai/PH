"""
Supabase REST API 테스트
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

def test_connection():
    print("="*60)
    print("🧪 Supabase REST API 연결 테스트")
    print("="*60)
    
    print(f"\nURL: {SUPABASE_URL}")
    print(f"Key: {SUPABASE_KEY[:20]}...")
    
    # 헤더 설정
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # 1. 테이블 조회 테스트
    print("\n1️⃣  데이터 조회 테스트...")
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/phishing_news",
            headers=headers,
            params={'limit': 5},
            timeout=10
        )
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 성공! 데이터 {len(data)}건 조회")
            if data:
                print(f"   첫 번째 항목: {data[0].get('title', '')[:50]}...")
        else:
            print(f"   ❌ 실패: {response.text}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    # 2. 데이터 삽입 테스트
    print("\n2️⃣  데이터 삽입 테스트...")
    test_data = {
        'source': 'test',
        'title': '테스트 뉴스',
        'content': '이것은 테스트 콘텐츠입니다.',
        'url': f'https://test.com/test_{os.getpid()}',
        'category': 'NEWS',
        'original_language': 'ko',
        'content_length': 20,
        'crawled_at': '2026-02-01T00:00:00'
    }
    
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/phishing_news",
            headers=headers,
            json=test_data,
            timeout=10
        )
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"   ✅ 성공! 테스트 데이터 삽입됨")
        else:
            print(f"   ❌ 실패: {response.text}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    print("\n" + "="*60)
    print("✅ 테스트 완료")
    print("="*60)

if __name__ == "__main__":
    test_connection()
