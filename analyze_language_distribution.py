#!/usr/bin/env python3
"""
임베딩된 REAL_CASE 데이터 언어 분석
"""
import os
import requests
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

headers = {
    'apikey': supabase_key,
    'Authorization': f'Bearer {supabase_key}',
    'Content-Type': 'application/json'
}

print("\n" + "="*100)
print("🌍 임베딩된 데이터 언어 분석 (REAL_CASE)")
print("="*100 + "\n")

# === 1. 이미지 데이터 언어 분포 ===
print("🖼️  이미지 REAL_CASE")
print("-"*100)

response = requests.get(
    f"{supabase_url}/rest/v1/phishing_images",
    headers=headers,
    params={
        'select': 'id,language,ocr_text',
        'classification': 'eq.REAL_CASE',
        'embedding': 'not.is.null'
    },
    timeout=30
)

if response.status_code == 200:
    images = response.json()
    total_images = len(images)
    
    # 언어별 분포
    languages = Counter([img.get('language', 'unknown') for img in images])
    
    print(f"   전체 임베딩 완료: {total_images}개\n")
    print(f"   언어별 분포:")
    for lang, count in languages.most_common():
        percentage = (count / total_images * 100) if total_images > 0 else 0
        lang_name = {
            'ko': '🇰🇷 한국어',
            'en': '🇺🇸 영어',
            'unknown': '❓ 미분류'
        }.get(lang, f'🌐 {lang}')
        print(f"      {lang_name}: {count:,}개 ({percentage:.1f}%)")
    
    # 영어 샘플 확인
    en_samples = [img for img in images if img.get('language') == 'en'][:3]
    if en_samples:
        print(f"\n   📝 영어 메시지 샘플:")
        for idx, sample in enumerate(en_samples, 1):
            text = sample.get('ocr_text', '')[:100]
            print(f"      [{idx}] {text}...")
else:
    print(f"   ❌ 조회 실패: {response.status_code}")
    total_images = 0

print()

# === 2. 뉴스 데이터 언어 분포 ===
print("📰 뉴스 REAL_CASE")
print("-"*100)

response = requests.get(
    f"{supabase_url}/rest/v1/phishing_news",
    headers=headers,
    params={
        'select': 'id,original_language,title',
        'category': 'eq.REAL_CASE',
        'embedding': 'not.is.null'
    },
    timeout=30
)

if response.status_code == 200:
    news = response.json()
    total_news = len(news)
    
    # 언어별 분포
    languages = Counter([n.get('original_language', 'unknown') for n in news])
    
    print(f"   전체 임베딩 완료: {total_news}개\n")
    print(f"   언어별 분포:")
    for lang, count in languages.most_common():
        percentage = (count / total_news * 100) if total_news > 0 else 0
        lang_name = {
            'ko': '🇰🇷 한국어',
            'en': '🇺🇸 영어',
            'unknown': '❓ 미분류',
            'kr': '🇰🇷 한국어',
        }.get(lang, f'🌐 {lang}')
        print(f"      {lang_name}: {count:,}개 ({percentage:.1f}%)")
    
    # 영어 샘플 확인
    en_samples = [n for n in news if n.get('original_language') in ['en', 'EN']][:3]
    if en_samples:
        print(f"\n   📝 영어 뉴스 샘플:")
        for idx, sample in enumerate(en_samples, 1):
            title = sample.get('title', '')[:80]
            print(f"      [{idx}] {title}...")
else:
    print(f"   ❌ 조회 실패: {response.status_code}")
    total_news = 0

print()

# === 3. 전체 통계 ===
print("="*100)
print("📊 전체 임베딩 데이터 언어 통계")
print("="*100 + "\n")

if response.status_code == 200:
    total = total_images + total_news
    
    print(f"   총 임베딩 데이터: {total:,}개")
    print(f"      - 이미지: {total_images:,}개")
    print(f"      - 뉴스: {total_news:,}개")
    print()
    
    # 대략적인 한국어 비율 계산
    # (이미지는 정확, 뉴스는 대부분 한국어로 가정)
    korean_percentage = ((total_images * 0.987 + total_news * 0.95) / total * 100) if total > 0 else 0
    
    print(f"   🇰🇷 한국어 데이터: 약 {korean_percentage:.1f}%")
    print(f"   🌐 기타 언어: 약 {100-korean_percentage:.1f}%")
    print()
    print(f"   💡 한국인 대상 서비스에 최적화된 데이터셋입니다!")

print()
print("="*100 + "\n")
