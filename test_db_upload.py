#!/usr/bin/env python3
"""
DB 업로드 테스트
"""
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# 테스트 데이터
test_data = {
    'image_url': 'https://phishing-images/test_dual_ocr.jpg',
    'local_path': 'data/images/phishing/test.jpg',
    'query': 'phishing',
    'ocr_text': '테스트 OCR 텍스트',
    'translated_text': '테스트 번역 텍스트',
    'language': 'ko',
    'text_length': 100,
    'ocr_model': 'openai',
    'crawled_at': datetime.now().isoformat(),
    'processed_at': datetime.now().isoformat()
}

print("\n" + "="*100)
print("🧪 DB 업로드 테스트")
print("="*100)
print(f"\nSupabase URL: {supabase_url}")
print(f"데이터: {test_data}")
print()

url = f"{supabase_url}/rest/v1/phishing_images"

response = requests.post(url, headers=headers, json=test_data, timeout=10)

print(f"Status Code: {response.status_code}")
print(f"\n응답:")
print(response.text)
print("\n" + "="*100)
