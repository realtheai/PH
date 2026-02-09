#!/usr/bin/env python3
"""
Retrieval 가능한 데이터 통계
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
    "Prefer": "count=exact"
}

def get_count(table, condition=""):
    """테이블 카운트 조회"""
    url = f"{supabase_url}/rest/v1/{table}?select=id&limit=1"
    if condition:
        url += f"&{condition}"
    
    response = requests.get(url, headers=headers, timeout=30)
    
    if response.status_code == 200:
        content_range = response.headers.get('Content-Range', '*/0')
        if '/' in content_range:
            return int(content_range.split('/')[1])
    return 0

print("\n" + "="*100)
print("📊 Retrieval 가능한 데이터 통계")
print("="*100 + "\n")

# === 뉴스 테이블 ===
print("📰 phishing_news (뉴스)")
print("-" * 100)

news_total = get_count("phishing_news")
news_embedded = get_count("phishing_news", "embedding=not.is.null")
news_classified = get_count("phishing_news", "category=not.is.null")

print(f"   전체 뉴스: {news_total}개")
print(f"   임베딩 완료: {news_embedded}개 ({news_embedded/news_total*100:.1f}%)" if news_total > 0 else "   임베딩 완료: 0개")
print(f"   분류 완료: {news_classified}개")
print()

# === 이미지 테이블 ===
print("🖼️  phishing_images (이미지)")
print("-" * 100)

images_total = get_count("phishing_images")
images_ocr = get_count("phishing_images", "ocr_text=not.is.null")
images_embedded = get_count("phishing_images", "embedding=not.is.null")
images_classified = get_count("phishing_images", "classification=not.is.null")

print(f"   전체 이미지: {images_total}개")
print(f"   OCR 완료: {images_ocr}개 ({images_ocr/images_total*100:.1f}%)" if images_total > 0 else "   OCR 완료: 0개")
print(f"   분류 완료: {images_classified}개 ({images_classified/images_total*100:.1f}%)" if images_total > 0 else "   분류 완료: 0개")
print(f"   임베딩 완료: {images_embedded}개 ({images_embedded/images_total*100:.1f}%)" if images_total > 0 else "   임베딩 완료: 0개")
print()

# === 분류별 통계 ===
print("🏷️  분류별 통계 (images)")
print("-" * 100)

real_case = get_count("phishing_images", "classification=eq.REAL_CASE")
news_class = get_count("phishing_images", "classification=eq.NEWS")
noise = get_count("phishing_images", "classification=eq.NOISE")

print(f"   🔴 REAL_CASE: {real_case}개")
print(f"   📰 NEWS: {news_class}개")
print(f"   ⚫ NOISE: {noise}개")
print()

# === Retrieval 가능 데이터 ===
print("="*100)
print("🔍 Retrieval 가능 데이터")
print("="*100)

total_embedded = news_embedded + images_embedded
total_data = news_total + images_total

print(f"   📊 전체 데이터: {total_data:,}개 (뉴스 {news_total:,}개 + 이미지 {images_total:,}개)")
print(f"   ✅ Retrieval 가능: {total_embedded:,}개 (뉴스 {news_embedded:,}개 + 이미지 {images_embedded:,}개)")
print(f"   📈 Retrieval 가능률: {total_embedded/total_data*100:.1f}%" if total_data > 0 else "   📈 Retrieval 가능률: 0%")
print()
print(f"   🎯 실제 피싱 케이스 (REAL_CASE): {real_case:,}개")
print("="*100 + "\n")
