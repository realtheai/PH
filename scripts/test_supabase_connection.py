#!/usr/bin/env python3
"""
Supabase 연결 및 테이블 존재 확인
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

print("\n" + "="*70)
print("🔍 Supabase 연결 테스트")
print("="*70 + "\n")

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_KEY: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "SUPABASE_KEY: None")
print()

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Supabase 환경 변수가 설정되지 않았습니다!")
    exit(1)

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

# 각 테이블에 대해 간단한 쿼리 시도
tables = ['phishing_news', 'phishing_images', 'phishing_reddit']

for table in tables:
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}?select=*&limit=1"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ {table}: 테이블 존재 (응답: {response.status_code})")
        elif response.status_code == 404:
            print(f"❌ {table}: 테이블이 존재하지 않음 (응답: {response.status_code})")
        else:
            print(f"⚠️  {table}: 알 수 없는 응답 (응답: {response.status_code})")
            print(f"   응답 내용: {response.text[:200]}")
    except Exception as e:
        print(f"❌ {table}: 오류 - {e}")

print("\n" + "="*70 + "\n")
