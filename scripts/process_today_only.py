#!/usr/bin/env python3
"""
오늘 크롤링한 데이터만 분류 및 임베딩 처리
"""
import os
import sys
import requests
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ANON_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

# 오늘 날짜 (UTC 기준)
today = datetime.utcnow().strftime('%Y-%m-%d')

print("\n" + "="*80)
print(f"🔍 오늘({today}) 크롤링한 데이터 확인")
print("="*80 + "\n")

# 1. 오늘 크롤링된 이미지 개수 확인
url = f"{SUPABASE_URL}/rest/v1/phishing_images"
params = {
    'select': 'id,ocr_text,classification',
    'created_at': f'gte.{today}',
    'order': 'id.asc'
}
response = requests.get(url, headers=HEADERS, params=params, timeout=30)

if response.status_code == 200:
    today_images = response.json()
    total_images = len(today_images)
    
    # 분류 필요한 이미지 (OCR은 있지만 classification이 없는 것)
    need_classification = [img for img in today_images if img.get('ocr_text') and not img.get('classification')]
    
    print(f"📸 오늘 이미지:")
    print(f"   전체: {total_images}개")
    print(f"   분류 필요: {len(need_classification)}개")
    print()
else:
    print(f"❌ 이미지 조회 실패: {response.status_code}")
    sys.exit(1)

# 2. 오늘 크롤링된 뉴스 개수 확인
url = f"{SUPABASE_URL}/rest/v1/phishing_news"
params = {
    'select': 'id,category,embedding',
    'created_at': f'gte.{today}',
    'order': 'id.asc'
}
response = requests.get(url, headers=HEADERS, params=params, timeout=30)

if response.status_code == 200:
    today_news = response.json()
    total_news = len(today_news)
    
    # 임베딩 필요한 뉴스
    need_embedding_news = [news for news in today_news if not news.get('embedding')]
    
    print(f"📰 오늘 뉴스:")
    print(f"   전체: {total_news}개")
    print(f"   임베딩 필요: {len(need_embedding_news)}개")
    print()
else:
    print(f"❌ 뉴스 조회 실패: {response.status_code}")
    sys.exit(1)

# 3. 처리 계획
print("="*80)
print("📋 처리 계획")
print("="*80)
print(f"1. 이미지 분류: {len(need_classification)}개")
print(f"2. 뉴스 임베딩: {len(need_embedding_news)}개")
print(f"3. 이미지 임베딩: {total_images}개 (분류 후)")
print()

total_tasks = len(need_classification) + len(need_embedding_news) + total_images
print(f"📊 총 작업: {total_tasks}개 항목")
print(f"⏱️  예상 시간: 약 {total_tasks // 60 + 1}분")
print()

# 4. 실행 확인
print("="*80)
response = input("실행하시겠습니까? (y/n): ")
if response.lower() != 'y':
    print("취소되었습니다.")
    sys.exit(0)

print("\n🚀 처리를 시작합니다...\n")

# 5. 각 스크립트 실행
import subprocess

scripts = []

if need_classification:
    print(f"1️⃣  이미지 분류 시작 ({len(need_classification)}개)...")
    result = subprocess.run(
        ['python', 'scripts/classify_data.py', '--date', today, '--type', 'images'],
        cwd='/home/realtheai/phishingapp',
        capture_output=False
    )
    if result.returncode == 0:
        print("✅ 이미지 분류 완료!\n")
    else:
        print("⚠️  이미지 분류 실패. 계속 진행합니다.\n")

if need_embedding_news:
    print(f"2️⃣  뉴스 임베딩 시작 ({len(need_embedding_news)}개)...")
    result = subprocess.run(
        ['python', 'scripts/run_full_embedding_openai.py', '--date', today, '--type', 'news'],
        cwd='/home/realtheai/phishingapp',
        capture_output=False
    )
    if result.returncode == 0:
        print("✅ 뉴스 임베딩 완료!\n")
    else:
        print("⚠️  뉴스 임베딩 실패. 계속 진행합니다.\n")

if total_images:
    print(f"3️⃣  이미지 임베딩 시작 ({total_images}개)...")
    result = subprocess.run(
        ['python', 'scripts/run_full_embedding_openai.py', '--date', today, '--type', 'images'],
        cwd='/home/realtheai/phishingapp',
        capture_output=False
    )
    if result.returncode == 0:
        print("✅ 이미지 임베딩 완료!\n")
    else:
        print("⚠️  이미지 임베딩 실패.\n")

print("\n" + "="*80)
print("🎉 모든 처리가 완료되었습니다!")
print("="*80 + "\n")
