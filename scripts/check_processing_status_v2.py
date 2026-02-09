#!/usr/bin/env python3
"""
데이터 처리 상태 확인 (수정 버전)
"""
import os
import requests
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ANON_KEY')
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

def get_all_data(table: str, columns: str = '*') -> list:
    """모든 데이터 조회 (페이지네이션)"""
    all_data = []
    offset = 0
    limit = 1000
    
    while True:
        url = f"{SUPABASE_URL}/rest/v1/{table}?select={columns}&limit={limit}&offset={offset}"
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            all_data.extend(data)
            offset += len(data)
            if len(data) < limit:
                break
        else:
            print(f"❌ 에러: {response.status_code} - {response.text}")
            break
    
    return all_data

print("\n" + "="*80)
print("🔍 데이터 처리 상태 확인")
print("="*80 + "\n")

# 1. phishing_news
print("1️⃣  phishing_news 테이블")
print("-" * 80)

news_data = get_all_data('phishing_news', 'id,classification,phishing_type,embedding,translated_content')
total_news = len(news_data)

classified_news = sum(1 for item in news_data if item.get('classification'))
typed_news = sum(1 for item in news_data if item.get('phishing_type'))
embedded_news = sum(1 for item in news_data if item.get('embedding'))
translated_news = sum(1 for item in news_data if item.get('translated_content'))

print(f"   전체: {total_news:,}개")
print(f"   번역: {translated_news:,}개 ({translated_news/max(total_news,1)*100:.1f}%)")
print(f"   분류: {classified_news:,}개 ({classified_news/max(total_news,1)*100:.1f}%)")
print(f"   타입: {typed_news:,}개 ({typed_news/max(total_news,1)*100:.1f}%)")
print(f"   임베딩: {embedded_news:,}개 ({embedded_news/max(total_news,1)*100:.1f}%)")

if classified_news > 0:
    classifications = Counter([item['classification'] for item in news_data if item.get('classification')])
    print(f"\n   분류별:")
    for cls, count in classifications.most_common():
        print(f"      - {cls}: {count:,}개")

print()

# 2. phishing_images
print("2️⃣  phishing_images 테이블")
print("-" * 80)

images_data = get_all_data('phishing_images', 'id,classification,phishing_type,embedding,ocr_text,translated_content')
total_images = len(images_data)

ocr_images = sum(1 for item in images_data if item.get('ocr_text'))
classified_images = sum(1 for item in images_data if item.get('classification'))
typed_images = sum(1 for item in images_data if item.get('phishing_type'))
embedded_images = sum(1 for item in images_data if item.get('embedding'))
translated_images = sum(1 for item in images_data if item.get('translated_content'))

print(f"   전체: {total_images:,}개")
print(f"   OCR: {ocr_images:,}개 ({ocr_images/max(total_images,1)*100:.1f}%)")
print(f"   번역: {translated_images:,}개 ({translated_images/max(total_images,1)*100:.1f}%)")
print(f"   분류: {classified_images:,}개 ({classified_images/max(total_images,1)*100:.1f}%)")
print(f"   타입: {typed_images:,}개 ({typed_images/max(total_images,1)*100:.1f}%)")
print(f"   임베딩: {embedded_images:,}개 ({embedded_images/max(total_images,1)*100:.1f}%)")

if classified_images > 0:
    img_classifications = Counter([item['classification'] for item in images_data if item.get('classification')])
    print(f"\n   분류별:")
    for cls, count in img_classifications.most_common():
        print(f"      - {cls}: {count:,}개")

print()

# 3. 전체 요약
print("="*80)
print("📈 전체 요약")
print("="*80)

total_all = total_news + total_images
total_translated = translated_news + translated_images
total_classified = classified_news + classified_images
total_typed = typed_news + typed_images
total_embedded = embedded_news + embedded_images

print(f"   전체 데이터: {total_all:,}개")
if total_all > 0:
    print(f"   번역 완료: {total_translated:,}개 ({total_translated/total_all*100:.1f}%)")
    print(f"   분류 완료: {total_classified:,}개 ({total_classified/total_all*100:.1f}%)")
    print(f"   타입 할당: {total_typed:,}개")
    print(f"   임베딩 생성: {total_embedded:,}개 ({total_embedded/total_all*100:.1f}%)")

print()

# 4. 누락된 단계
print("="*80)
print("⚠️  누락된 처리 단계")
print("="*80)

steps_needed = []

if ocr_images < total_images:
    steps_needed.append(f"OCR: {total_images - ocr_images:,}개 이미지")

if total_translated < total_all:
    steps_needed.append(f"번역: {total_all - total_translated:,}개")

if total_classified < total_all:
    steps_needed.append(f"분류: {total_all - total_classified:,}개")

if total_typed < total_classified:
    steps_needed.append(f"피싱타입: {total_classified - total_typed:,}개")

if total_embedded < total_all:
    steps_needed.append(f"임베딩: {total_all - total_embedded:,}개")

if steps_needed:
    for i, step in enumerate(steps_needed, 1):
        print(f"   {i}. {step}")
    print()
    print("💡 다음 명령으로 누락된 단계를 실행하세요:")
    print("   python scripts/run_missing_pipeline.py")
else:
    print("   ✅ 모든 처리가 완료되었습니다!")

print("\n" + "="*80 + "\n")
