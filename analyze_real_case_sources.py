#!/usr/bin/env python3
"""
REAL_CASE 데이터 소스별 분석
"""
import os
import requests
from collections import Counter
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
print("🔍 REAL_CASE 데이터 소스별 분석")
print("="*100 + "\n")

# === 1. 이미지 테이블 (phishing_images) ===
print("📊 이미지 데이터 (phishing_images)")
print("-"*100)

url = f"{supabase_url}/rest/v1/phishing_images"
params = {
    "select": "id,query,source,classification,local_path",
    "classification": "eq.REAL_CASE"
}

response = requests.get(url, headers=headers, params=params, timeout=30)

if response.status_code == 200:
    images_data = response.json()
    total_images = len(images_data)
    
    # 소스별 분포
    image_sources = Counter([item.get('source', 'unknown') for item in images_data])
    
    # 쿼리별 분포 (검색 키워드)
    image_queries = Counter([item.get('query', 'unknown') for item in images_data])
    
    print(f"   총 REAL_CASE 이미지: {total_images}개\n")
    
    print("   📁 소스별 분포:")
    for source, count in image_sources.most_common():
        print(f"      - {source}: {count}개 ({count/total_images*100:.1f}%)")
    print()
    
    print("   🔎 검색 쿼리별 분포 (상위 10개):")
    for query, count in image_queries.most_common(10):
        print(f"      - '{query}': {count}개")
    print()

else:
    print(f"   ❌ 오류: {response.status_code}")
    print(f"   {response.text}\n")
    total_images = 0

# === 2. 뉴스 테이블 (phishing_news) ===
print("="*100)
print("📰 뉴스 데이터 (phishing_news)")
print("-"*100)

url = f"{supabase_url}/rest/v1/phishing_news"
params = {
    "select": "id,source,title,category,url"
}

response = requests.get(url, headers=headers, params=params, timeout=30)

if response.status_code == 200:
    news_data = response.json()
    total_news = len(news_data)
    
    # 소스별 분포
    news_sources = Counter([item.get('source', 'unknown') for item in news_data])
    
    # 카테고리별 분포
    news_categories = Counter([item.get('category', 'unknown') for item in news_data])
    
    print(f"   총 뉴스: {total_news}개\n")
    
    print("   📁 소스별 분포:")
    for source, count in news_sources.most_common():
        print(f"      - {source}: {count}개 ({count/total_news*100:.1f}%)")
    print()
    
    print("   🏷️  카테고리별 분포:")
    for category, count in news_categories.most_common():
        print(f"      - {category}: {count}개 ({count/total_news*100:.1f}%)")
    print()
    
    # REAL_CASE에 해당하는 카테고리 찾기
    real_case_categories = ['REAL_CASE', 'phishing', 'fraud', 'scam', '피싱', '보이스피싱', '스미싱']
    real_news = [item for item in news_data if any(cat in str(item.get('category', '')).lower() for cat in [c.lower() for c in real_case_categories])]
    
    if real_news:
        print(f"   🔴 피싱 관련 뉴스 (추정): {len(real_news)}개")
        real_news_sources = Counter([item.get('source', 'unknown') for item in real_news])
        for source, count in real_news_sources.most_common():
            print(f"      - {source}: {count}개")
        print()

else:
    print(f"   ❌ 오류: {response.status_code}")
    print(f"   {response.text}\n")
    total_news = 0

# === 전체 요약 ===
print("="*100)
print("📊 전체 REAL_CASE 데이터 요약")
print("="*100)
print()
print(f"   🖼️  이미지 (REAL_CASE): {total_images}개")

if response.status_code == 200:
    print(f"   📰 뉴스 (전체): {total_news}개")
    if real_news:
        print(f"   📰 뉴스 (피싱 관련 추정): {len(real_news)}개")

print()
print("   📁 데이터 소스 구성:")

# 이미지 소스
if total_images > 0:
    print(f"\n   [이미지 소스]")
    for source, count in image_sources.most_common():
        print(f"      - {source}: {count}개")

# 뉴스 소스
if total_news > 0:
    print(f"\n   [뉴스 소스]")
    for source, count in news_sources.most_common():
        print(f"      - {source}: {count}개")

print()
print("="*100 + "\n")
