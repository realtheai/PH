#!/usr/bin/env python3
"""
실제 피싱 케이스 데이터 조회
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}

print("\n" + "="*100)
print("🔴 실제 피싱 케이스 (REAL_CASE) 데이터")
print("="*100 + "\n")

# REAL_CASE 데이터 조회
url = f"{supabase_url}/rest/v1/phishing_images"
params = {
    "select": "id,query,local_path,ocr_text,translated_text,language,classification,phishing_type,created_at",
    "classification": "eq.REAL_CASE",
    "order": "created_at.desc",
    "limit": 50  # 처음 50개만
}

response = requests.get(url, headers=headers, params=params, timeout=30)

if response.status_code == 200:
    data = response.json()
    print(f"📊 조회된 데이터: {len(data)}개 (전체 중 처음 50개)\n")
    
    for idx, item in enumerate(data, 1):
        print(f"\n{'='*100}")
        print(f"[{idx}] ID: {item['id']}")
        print(f"{'='*100}")
        print(f"🔍 검색 쿼리: {item.get('query', 'N/A')}")
        print(f"📁 파일 경로: {item.get('local_path', 'N/A')}")
        print(f"🌐 언어: {item.get('language', 'N/A')}")
        print(f"🏷️  분류: {item.get('classification', 'N/A')}")
        print(f"📅 생성일: {item.get('created_at', 'N/A')}")
        
        if item.get('phishing_type'):
            print(f"⚠️  피싱 유형: {item['phishing_type']}")
        
        print(f"\n📝 OCR 텍스트:")
        ocr_text = item.get('ocr_text', '')
        if ocr_text:
            # 긴 텍스트는 처음 300자만
            if len(ocr_text) > 300:
                print(f"   {ocr_text[:300]}...")
            else:
                print(f"   {ocr_text}")
        else:
            print("   (없음)")
        
        if item.get('translated_text'):
            print(f"\n🌏 번역 텍스트:")
            translated = item['translated_text']
            if len(translated) > 300:
                print(f"   {translated[:300]}...")
            else:
                print(f"   {translated}")
    
    print(f"\n{'='*100}")
    print(f"✅ 총 {len(data)}개의 실제 피싱 케이스 표시 완료 (전체 373개 중)")
    print("="*100 + "\n")
    
else:
    print(f"❌ 오류: {response.status_code}")
    print(f"   {response.text}")
