#!/usr/bin/env python3
"""
Supabase 데이터베이스 상세 확인
"""
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

def get_count(table: str, filter_query: str = "") -> int:
    """레코드 수 조회"""
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*&{filter_query}"
    headers_with_count = {**HEADERS, 'Prefer': 'count=exact'}
    try:
        response = requests.get(url, headers=headers_with_count, timeout=10)
        if response.status_code == 200:
            return int(response.headers.get('Content-Range', '0-0/0').split('/')[-1])
        elif response.status_code == 404:
            return -1  # 테이블이 없음
    except Exception as e:
        print(f"❌ 에러: {e}")
    return 0

def get_sample_data(table: str, limit: int = 3) -> list:
    """샘플 데이터 조회"""
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*&limit={limit}&order=created_at.desc"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
    except Exception as e:
        print(f"❌ 에러: {e}")
    return []

def get_latest_record(table: str) -> dict:
    """가장 최근 레코드 조회"""
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*&limit=1&order=created_at.desc"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data[0] if data else None
    except Exception as e:
        pass
    return None

def check_table_structure(table: str):
    """테이블 구조 확인 (샘플 데이터로부터 추론)"""
    sample = get_sample_data(table, limit=1)
    if sample is None:
        return None
    if sample and len(sample) > 0:
        return list(sample[0].keys())
    return []

print("\n" + "="*80)
print("🔍 Supabase 데이터베이스 상세 확인")
print("="*80 + "\n")

print(f"📍 Supabase URL: {SUPABASE_URL}")
print(f"🔑 API Key: {SUPABASE_KEY[:30]}...\n")

# 확인할 테이블 목록
tables = {
    'phishing_news': '뉴스 데이터',
    'phishing_images': '이미지 데이터',
    'phishing_reddit': 'Reddit 데이터'
}

for table_name, description in tables.items():
    print("="*80)
    print(f"📊 {description} ({table_name})")
    print("="*80)
    
    # 1. 테이블 존재 여부 및 레코드 수
    count = get_count(table_name)
    
    if count == -1:
        print(f"❌ 테이블이 존재하지 않습니다!\n")
        continue
    
    print(f"📈 총 레코드 수: {count:,}개\n")
    
    if count == 0:
        print("⚠️  데이터가 없습니다.\n")
        # 테이블 구조는 확인 가능
        columns = check_table_structure(table_name)
        if columns:
            print(f"📋 테이블 컬럼: {', '.join(columns)}\n")
        continue
    
    # 2. 테이블 구조
    columns = check_table_structure(table_name)
    if columns:
        print(f"📋 테이블 컬럼 ({len(columns)}개):")
        for col in columns:
            print(f"   - {col}")
        print()
    
    # 3. 최근 데이터 정보
    latest = get_latest_record(table_name)
    if latest:
        print(f"🕐 최근 데이터:")
        print(f"   - ID: {latest.get('id', 'N/A')}")
        print(f"   - Created: {latest.get('created_at', 'N/A')}")
        
        if table_name == 'phishing_news':
            print(f"   - Title: {latest.get('title', 'N/A')[:50]}...")
            print(f"   - Source: {latest.get('source', 'N/A')}")
            print(f"   - Classification: {latest.get('classification', 'N/A')}")
            print(f"   - Phishing Type: {latest.get('phishing_type', 'N/A')}")
            print(f"   - Has Embedding: {'✅' if latest.get('embedding') else '❌'}")
            print(f"   - Translated: {'✅' if latest.get('translated_content') else '❌'}")
        
        elif table_name == 'phishing_images':
            print(f"   - Image URL: {latest.get('image_url', 'N/A')[:60]}...")
            print(f"   - Query: {latest.get('query', 'N/A')}")
            print(f"   - Source: {latest.get('source', 'N/A')}")
            print(f"   - OCR Text: {latest.get('ocr_text', 'N/A')[:50] if latest.get('ocr_text') else '❌'}...")
            print(f"   - Classification: {latest.get('classification', 'N/A')}")
            print(f"   - Phishing Type: {latest.get('phishing_type', 'N/A')}")
            print(f"   - Has Embedding: {'✅' if latest.get('embedding') else '❌'}")
        
        elif table_name == 'phishing_reddit':
            print(f"   - Title: {latest.get('title', 'N/A')[:50]}...")
            print(f"   - Subreddit: {latest.get('subreddit', 'N/A')}")
            print(f"   - Classification: {latest.get('classification', 'N/A')}")
    
    print()
    
    # 4. 분류별 통계 (있다면)
    if count > 0:
        print("📊 분류별 통계:")
        for classification in ['REAL_CASE', 'NEWS', 'NOISE']:
            class_count = get_count(table_name, f"classification=eq.{classification}")
            if class_count > 0:
                print(f"   - {classification}: {class_count:,}개")
        
        print()
        
        # 5. 처리 상태 통계
        print("⚙️  처리 상태:")
        translated = get_count(table_name, "translated_content=not.is.null")
        classified = get_count(table_name, "classification=not.is.null")
        typed = get_count(table_name, "phishing_type=not.is.null")
        embedded = get_count(table_name, "embedding=not.is.null")
        
        print(f"   - 번역 완료: {translated:,}개 ({translated/count*100:.1f}%)")
        print(f"   - 분류 완료: {classified:,}개 ({classified/count*100:.1f}%)")
        print(f"   - 타입 할당: {typed:,}개 ({typed/count*100:.1f}%)")
        print(f"   - 임베딩 생성: {embedded:,}개 ({embedded/count*100:.1f}%)")
        
        print()

print("="*80)
print("✅ 확인 완료")
print("="*80 + "\n")
