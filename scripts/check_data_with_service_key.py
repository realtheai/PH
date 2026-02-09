#!/usr/bin/env python3
"""
RLS 우회하여 데이터 확인 (서비스 키 필요)
"""
import os
import requests
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
# ANON KEY 대신 다른 방법 시도
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

print("\n" + "="*80)
print("🔍 Supabase 데이터 상세 확인 (RLS 고려)")
print("="*80 + "\n")

# API로 직접 확인 (RLS 정책 무시하는 쿼리)
def check_via_sql_query(query: str):
    """SQL 쿼리 실행"""
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {'query': query}
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    return response

print("📋 Supabase 대시보드에서 확인된 데이터:")
print("   - phishing_images: 2,837개")
print("   - phishing_news: 4,687개")
print()

print("="*80)
print("💡 데이터 확인 방법")
print("="*80)
print()
print("1️⃣  **Supabase 대시보드에서 직접 확인** (추천)")
print(f"   {SUPABASE_URL.replace('/rest/v1', '')}")
print()
print("   👉 왼쪽 메뉴 'Tables' 클릭")
print("   👉 'phishing_news' 또는 'phishing_images' 클릭")
print("   👉 데이터 행들이 표시됩니다")
print()
print("2️⃣  **SQL Editor에서 쿼리 실행**")
print("   왼쪽 메뉴 'SQL Editor' → 다음 쿼리 실행:")
print()
print("   -- 뉴스 데이터 샘플 확인")
print("   SELECT id, title, source, classification, phishing_type, ")
print("          created_at, embedding IS NOT NULL as has_embedding")
print("   FROM phishing_news")
print("   ORDER BY created_at DESC")
print("   LIMIT 10;")
print()
print("   -- 이미지 데이터 샘플 확인")
print("   SELECT id, query, source, ocr_text, classification, ")
print("          phishing_type, created_at")
print("   FROM phishing_images")
print("   ORDER BY created_at DESC")
print("   LIMIT 10;")
print()
print("   -- 분류별 통계")
print("   SELECT classification, COUNT(*) as count")
print("   FROM phishing_news")
print("   WHERE classification IS NOT NULL")
print("   GROUP BY classification;")
print()
print("   -- 처리 진행률")
print("   SELECT ")
print("     COUNT(*) as total,")
print("     COUNT(classification) as classified,")
print("     COUNT(phishing_type) as typed,")
print("     COUNT(embedding) as embedded")
print("   FROM phishing_news;")
print()
print("="*80)
print()
print("💬 다음에 무엇을 하시겠습니까?")
print()
print("   A) 데이터 처리 상태 확인 (번역, 분류, 임베딩)")
print("   B) 누락된 처리 단계 실행")
print("   C) Reddit 테이블 생성 및 데이터 수집")
print("   D) 전체 파이프라인 재실행")
print()
print("="*80 + "\n")
