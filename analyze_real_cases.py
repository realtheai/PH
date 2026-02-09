#!/usr/bin/env python3
"""
실제 피싱 케이스 데이터 분석 및 샘플 조회
"""
import os
import requests
import json
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
print("🔴 실제 피싱 케이스 (REAL_CASE) 분석")
print("="*100 + "\n")

# 전체 REAL_CASE 데이터 조회
url = f"{supabase_url}/rest/v1/phishing_images"
params = {
    "select": "id,query,local_path,ocr_text,translated_text,language,classification,phishing_type,text_length",
    "classification": "eq.REAL_CASE"
}

response = requests.get(url, headers=headers, params=params, timeout=60)

if response.status_code == 200:
    data = response.json()
    total_count = len(data)
    
    print(f"📊 전체 REAL_CASE 데이터: {total_count}개\n")
    
    # === 통계 분석 ===
    print("="*100)
    print("📈 통계 분석")
    print("="*100 + "\n")
    
    # 언어별 분포
    languages = Counter([item.get('language', 'unknown') for item in data])
    print("🌐 언어별 분포:")
    for lang, count in languages.most_common():
        print(f"   {lang}: {count}개 ({count/total_count*100:.1f}%)")
    print()
    
    # 피싱 유형별 분포 (있는 경우)
    phishing_types = [item.get('phishing_type') for item in data if item.get('phishing_type')]
    if phishing_types:
        type_counter = Counter(phishing_types)
        print("⚠️  피싱 유형별 분포:")
        for ptype, count in type_counter.most_common():
            print(f"   {ptype}: {count}개")
        print()
    
    # 텍스트 길이 통계
    text_lengths = [item.get('text_length', 0) for item in data if item.get('text_length')]
    if text_lengths:
        avg_length = sum(text_lengths) / len(text_lengths)
        max_length = max(text_lengths)
        min_length = min(text_lengths)
        print(f"📝 텍스트 길이 통계:")
        print(f"   평균: {avg_length:.1f}자")
        print(f"   최대: {max_length}자")
        print(f"   최소: {min_length}자")
        print()
    
    # OCR/번역 완료 현황
    has_ocr = len([item for item in data if item.get('ocr_text')])
    has_translated = len([item for item in data if item.get('translated_text')])
    print(f"✅ 처리 완료 현황:")
    print(f"   OCR 완료: {has_ocr}개 ({has_ocr/total_count*100:.1f}%)")
    print(f"   번역 완료: {has_translated}개 ({has_translated/total_count*100:.1f}%)")
    print()
    
    # === 샘플 데이터 표시 ===
    print("="*100)
    print("📋 샘플 데이터 (10개)")
    print("="*100 + "\n")
    
    # 다양한 케이스 샘플링
    samples = []
    
    # 영어 케이스
    en_cases = [item for item in data if item.get('language') == 'en']
    if en_cases:
        samples.extend(en_cases[:3])
    
    # 한국어 케이스
    ko_cases = [item for item in data if item.get('language') == 'ko']
    if ko_cases:
        samples.extend(ko_cases[:5])
    
    # 기타
    other_cases = [item for item in data if item.get('language') not in ['en', 'ko']]
    if other_cases:
        samples.extend(other_cases[:2])
    
    for idx, item in enumerate(samples[:10], 1):
        print(f"\n{'─'*100}")
        print(f"[샘플 {idx}] 언어: {item.get('language', 'N/A').upper()}")
        print(f"{'─'*100}")
        print(f"📁 파일: {item.get('local_path', 'N/A').split('/')[-1]}")
        
        ocr_text = item.get('ocr_text', '')
        if ocr_text:
            # 길이에 따라 출력
            if len(ocr_text) > 200:
                print(f"\n📝 OCR: {ocr_text[:200]}... (총 {len(ocr_text)}자)")
            else:
                print(f"\n📝 OCR: {ocr_text}")
        
        translated = item.get('translated_text', '')
        if translated and item.get('language') == 'en':
            if len(translated) > 200:
                print(f"🌏 번역: {translated[:200]}... (총 {len(translated)}자)")
            else:
                print(f"🌏 번역: {translated}")
    
    print(f"\n{'='*100}")
    print(f"✅ 총 {total_count}개의 실제 피싱 케이스 데이터 분석 완료")
    print("="*100 + "\n")
    
else:
    print(f"❌ 오류: {response.status_code}")
    print(f"   {response.text}")
