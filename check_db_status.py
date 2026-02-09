#!/usr/bin/env python3
"""
DB 이미지 OCR 상태 확인
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json",
}

print("\n" + "="*100)
print("📊 DB 이미지 OCR 처리 상태 확인")
print("="*100 + "\n")

# 전체 이미지 수
response = requests.get(
    f"{supabase_url}/rest/v1/phishing_images?select=id",
    headers={**headers, "Prefer": "count=exact"},
    timeout=30
)

if response.status_code == 200:
    content_range = response.headers.get('Content-Range', '*/0')
    if '/' in content_range:
        total_count = int(content_range.split('/')[1])
    else:
        total_count = len(response.json())
    print(f"📌 전체 이미지: {total_count}개")
else:
    print(f"❌ 전체 조회 실패: {response.status_code} - {response.text[:200]}")
    total_count = 0

# OCR 성공 (ocr_text가 있는 것)
response = requests.get(
    f"{supabase_url}/rest/v1/phishing_images?select=id&ocr_text=not.is.null",
    headers={**headers, "Prefer": "count=exact"},
    timeout=30
)

if response.status_code == 200:
    content_range = response.headers.get('Content-Range', '*/0')
    if '/' in content_range:
        success_count = int(content_range.split('/')[1])
    else:
        success_count = len(response.json())
    print(f"✅ OCR 성공: {success_count}개 ({success_count/total_count*100:.1f}%)" if total_count > 0 else f"✅ OCR 성공: {success_count}개")
else:
    print(f"❌ OCR 성공 조회 실패: {response.status_code}")
    success_count = 0

# OCR 실패 (ocr_text가 null인 것)
response = requests.get(
    f"{supabase_url}/rest/v1/phishing_images?select=id&ocr_text=is.null",
    headers={**headers, "Prefer": "count=exact"},
    timeout=30
)

if response.status_code == 200:
    content_range = response.headers.get('Content-Range', '*/0')
    if '/' in content_range:
        failed_count = int(content_range.split('/')[1])
    else:
        failed_count = len(response.json())
    print(f"❌ OCR 실패 (미처리): {failed_count}개 ({failed_count/total_count*100:.1f}%)" if total_count > 0 else f"❌ OCR 실패: {failed_count}개")
else:
    print(f"❌ OCR 실패 조회 실패: {response.status_code}")
    failed_count = 0

# 번역된 것
response = requests.get(
    f"{supabase_url}/rest/v1/phishing_images?select=id&translated_text=not.is.null",
    headers={**headers, "Prefer": "count=exact"},
    timeout=30
)

if response.status_code == 200:
    content_range = response.headers.get('Content-Range', '*/0')
    if '/' in content_range:
        translated_count = int(content_range.split('/')[1])
    else:
        translated_count = len(response.json())
    print(f"🌐 번역 완료: {translated_count}개")
else:
    translated_count = 0

# 분류된 것 (classification이 있는 것)
response = requests.get(
    f"{supabase_url}/rest/v1/phishing_images?select=id&classification=not.is.null",
    headers={**headers, "Prefer": "count=exact"},
    timeout=30
)

if response.status_code == 200:
    content_range = response.headers.get('Content-Range', '*/0')
    if '/' in content_range:
        classified_count = int(content_range.split('/')[1])
    else:
        classified_count = len(response.json())
    print(f"🏷️  분류 완료: {classified_count}개")
else:
    classified_count = 0

# 임베딩된 것
response = requests.get(
    f"{supabase_url}/rest/v1/phishing_images?select=id&embedding=not.is.null",
    headers={**headers, "Prefer": "count=exact"},
    timeout=30
)

if response.status_code == 200:
    content_range = response.headers.get('Content-Range', '*/0')
    if '/' in content_range:
        embedded_count = int(content_range.split('/')[1])
    else:
        embedded_count = len(response.json())
    print(f"🔢 임베딩 완료: {embedded_count}개")
else:
    embedded_count = 0

print("\n" + "="*100)
print("📋 다음 단계 진행 가능 여부")
print("="*100)
print(f"1️⃣ OCR 처리: {success_count}/{total_count} ({'완료' if failed_count == 0 else f'{failed_count}개 남음'})")
print(f"2️⃣ 분류 처리: {classified_count}/{success_count} OCR 성공 이미지")
print(f"3️⃣ 임베딩 처리: {embedded_count}/{success_count} OCR 성공 이미지")
print("="*100 + "\n")
