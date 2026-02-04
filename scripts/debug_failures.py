"""
실패 원인 분석 스크립트
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

def test_insert_samples():
    print("="*60)
    print("🔍 실패 원인 분석")
    print("="*60)
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    # 1. 네이버 데이터 테스트
    print("\n1️⃣  네이버 데이터 테스트:")
    with open('data/raw/naver_api_2025-02-01_to_2026-01-31_fixed.json', 'r') as f:
        naver_data = json.load(f)
    
    # 실패 가능성 높은 항목 찾기
    test_item = naver_data[1700]  # 실패가 시작된 부근
    
    print(f"   테스트 항목: {test_item['title'][:50]}...")
    print(f"   URL: {test_item.get('url', 'NONE')}")
    print(f"   Content 길이: {len(test_item.get('content', ''))}")
    
    record = {
        'source': 'naver',
        'title': test_item['title'],
        'content': test_item.get('content', ''),
        'url': test_item['url'],
        'category': 'NEWS',
        'original_language': 'ko',
        'content_length': len(test_item.get('content', '')),
        'published_at': test_item.get('date'),
        'crawled_at': test_item['crawled_at']
    }
    
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/phishing_news",
            headers=headers,
            json=record,
            timeout=10
        )
        print(f"   응답 코드: {response.status_code}")
        print(f"   응답: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    # 2. 구글 뉴스 테스트
    print("\n2️⃣  구글 뉴스 테스트:")
    with open('data/raw/google_news_2025-02-01_to_2026-01-31.json', 'r') as f:
        google_data = json.load(f)
    
    test_item = google_data[50]  # 실패 항목
    
    print(f"   테스트 항목: {test_item['title'][:50]}...")
    print(f"   URL: {test_item.get('url', 'NONE')}")
    print(f"   Content: '{test_item.get('content', '')[:100]}'")
    
    record = {
        'source': 'google',
        'title': test_item['title'],
        'content': test_item.get('content', ''),
        'url': test_item['url'],
        'category': 'NEWS',
        'original_language': 'ko',
        'content_length': len(test_item.get('content', '')),
        'published_at': test_item.get('published_at'),
        'crawled_at': test_item['crawled_at']
    }
    
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/phishing_news",
            headers=headers,
            json=record,
            timeout=10
        )
        print(f"   응답 코드: {response.status_code}")
        print(f"   응답: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    # 3. Reddit 테스트
    print("\n3️⃣  Reddit 테스트:")
    with open('data/raw/reddit_2025-02-01_to_2026-01-31.json', 'r') as f:
        reddit_data = json.load(f)
    
    test_item = reddit_data[50]
    
    print(f"   테스트 항목: {test_item['title'][:50]}...")
    print(f"   URL: {test_item.get('url', 'NONE')}")
    
    record = {
        'source': 'reddit',
        'title': test_item['title'],
        'content': test_item.get('content', ''),
        'url': test_item['url'],
        'category': 'NEWS',
        'original_language': 'en',
        'content_length': len(test_item.get('content', '')),
        'published_at': test_item.get('published_at'),
        'crawled_at': test_item['crawled_at']
    }
    
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/phishing_news",
            headers=headers,
            json=record,
            timeout=10
        )
        print(f"   응답 코드: {response.status_code}")
        print(f"   응답: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")

if __name__ == "__main__":
    test_insert_samples()
