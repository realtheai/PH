#!/usr/bin/env python3
"""
전체 데이터 처리 마스터 스크립트
Solar(분류) + BGE-M3(임베딩) + OpenAI(번역)
"""
import requests
import json
import time
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

HEADERS = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

def get_data_status():
    """현재 데이터 처리 상태 확인"""
    print("\n" + "="*80)
    print("📊 현재 데이터 상태 확인")
    print("="*80 + "\n")
    
    # phishing_news
    news_resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/phishing_news",
        headers=HEADERS,
        params={'select': 'id,source,translated_content,category,phishing_type,embedding'}
    )
    
    if news_resp.status_code == 200:
        news = news_resp.json()
        total_news = len(news)
        
        needs_translation = sum(1 for n in news if n.get('source') in ['google_intl', 'reddit'] 
                               and not n.get('translated_content'))
        has_category = sum(1 for n in news if n.get('category'))
        needs_phishing_type = sum(1 for n in news if n.get('category') == 'REAL_CASE' 
                                  and not n.get('phishing_type'))
        has_embedding = sum(1 for n in news if n.get('embedding'))
        
        print(f"📰 뉴스: {total_news:,}개")
        print(f"   1️⃣ 번역 필요: {needs_translation:,}개")
        print(f"   2️⃣ 분류 필요: {total_news - has_category:,}개")
        print(f"   3️⃣ 피싱타입 필요: {needs_phishing_type:,}개")
        print(f"   4️⃣ 임베딩 필요: {total_news - has_embedding:,}개")
    else:
        print(f"❌ 뉴스 조회 실패: {news_resp.status_code}")
        total_news = 0
        needs_translation = 0
        has_category = 0
        needs_phishing_type = 0
        has_embedding = 0
    
    print()
    
    # phishing_images
    images_resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/phishing_images",
        headers=HEADERS,
        params={'select': 'id,ocr_text,translated_content,classification,phishing_type,embedding'}
    )
    
    if images_resp.status_code == 200:
        images = images_resp.json()
        total_images = len(images)
        
        needs_translation_img = sum(1 for i in images if i.get('ocr_text') 
                                   and not i.get('translated_content'))
        has_classification = sum(1 for i in images if i.get('classification'))
        needs_phishing_type_img = sum(1 for i in images if i.get('classification') == 'REAL_CASE' 
                                      and not i.get('phishing_type'))
        has_embedding_img = sum(1 for i in images if i.get('embedding'))
        
        print(f"🖼️ 이미지: {total_images:,}개")
        print(f"   1️⃣ 번역 필요: {needs_translation_img:,}개")
        print(f"   2️⃣ 분류 필요: {total_images - has_classification:,}개")
        print(f"   3️⃣ 피싱타입 필요: {needs_phishing_type_img:,}개")
        print(f"   4️⃣ 임베딩 필요: {total_images - has_embedding_img:,}개")
    else:
        print(f"❌ 이미지 조회 실패: {images_resp.status_code}")
        total_images = 0
        needs_translation_img = 0
        has_classification = 0
        needs_phishing_type_img = 0
        has_embedding_img = 0
    
    print()
    print("="*80)
    
    return {
        'news': {
            'total': total_news,
            'needs_translation': needs_translation,
            'needs_classification': total_news - has_category,
            'needs_phishing_type': needs_phishing_type,
            'needs_embedding': total_news - has_embedding
        },
        'images': {
            'total': total_images,
            'needs_translation': needs_translation_img,
            'needs_classification': total_images - has_classification,
            'needs_phishing_type': needs_phishing_type_img,
            'needs_embedding': total_images - has_embedding_img
        }
    }

def main():
    print("\n" + "="*80)
    print("🚀 전체 데이터 처리 시작")
    print("="*80)
    print("\n💡 처리 전략:")
    print("   1단계: 번역 (OpenAI GPT-4o-mini)")
    print("   2단계: 분류 (Solar 10.7B)")
    print("   3단계: 피싱 타입 (Solar 10.7B)")
    print("   4단계: 임베딩 (BGE-M3)")
    print()
    
    status = get_data_status()
    
    total_tasks = (
        status['news']['needs_translation'] +
        status['news']['needs_classification'] +
        status['news']['needs_phishing_type'] +
        status['news']['needs_embedding'] +
        status['images']['needs_translation'] +
        status['images']['needs_classification'] +
        status['images']['needs_phishing_type'] +
        status['images']['needs_embedding']
    )
    
    print(f"\n📊 총 처리 작업: {total_tasks:,}개\n")
    
    if total_tasks == 0:
        print("✅ 처리할 데이터가 없습니다!")
        return
    
    print("="*80)
    print("🎯 처리 순서")
    print("="*80 + "\n")
    
    steps = []
    
    if status['news']['needs_translation'] > 0:
        steps.append(f"1️⃣ 뉴스 번역 (OpenAI): {status['news']['needs_translation']:,}개")
    
    if status['images']['needs_translation'] > 0:
        steps.append(f"2️⃣ 이미지 번역 (OpenAI): {status['images']['needs_translation']:,}개")
    
    if status['news']['needs_classification'] > 0:
        steps.append(f"3️⃣ 뉴스 분류 (Solar): {status['news']['needs_classification']:,}개")
    
    if status['images']['needs_classification'] > 0:
        steps.append(f"4️⃣ 이미지 분류 (Solar): {status['images']['needs_classification']:,}개")
    
    if status['news']['needs_phishing_type'] > 0:
        steps.append(f"5️⃣ 뉴스 피싱타입 (Solar): {status['news']['needs_phishing_type']:,}개")
    
    if status['images']['needs_phishing_type'] > 0:
        steps.append(f"6️⃣ 이미지 피싱타입 (Solar): {status['images']['needs_phishing_type']:,}개")
    
    if status['news']['needs_embedding'] > 0:
        steps.append(f"7️⃣ 뉴스 임베딩 (BGE-M3): {status['news']['needs_embedding']:,}개")
    
    if status['images']['needs_embedding'] > 0:
        steps.append(f"8️⃣ 이미지 임베딩 (BGE-M3): {status['images']['needs_embedding']:,}개")
    
    for step in steps:
        print(step)
    
    print()
    print("="*80)
    print("💰 예상 비용 (OpenAI 번역만)")
    print("="*80)
    
    total_translation = status['news']['needs_translation'] + status['images']['needs_translation']
    estimated_cost = total_translation * 0.0001  # 평균 $0.0001/건
    
    print(f"   번역: {total_translation:,}개 × $0.0001 ≈ ${estimated_cost:.2f}")
    print(f"   분류/피싱타입/임베딩: Ollama (무료)")
    
    print()
    print("="*80)
    print("⏱️ 예상 소요 시간")
    print("="*80)
    
    # 번역: 1.2초/건, 분류: 8초/건, 피싱타입: 8초/건, 임베딩: 0.05초/건
    translation_time = total_translation * 1.2
    classification_time = (status['news']['needs_classification'] + 
                          status['images']['needs_classification']) * 8
    phishing_type_time = (status['news']['needs_phishing_type'] + 
                         status['images']['needs_phishing_type']) * 8
    embedding_time = (status['news']['needs_embedding'] + 
                     status['images']['needs_embedding']) * 0.05
    
    total_seconds = translation_time + classification_time + phishing_type_time + embedding_time
    total_minutes = total_seconds / 60
    total_hours = total_minutes / 60
    
    print(f"   번역:      {translation_time/60:.1f}분")
    print(f"   분류:      {classification_time/60:.1f}분")
    print(f"   피싱타입:  {phishing_type_time/60:.1f}분")
    print(f"   임베딩:    {embedding_time/60:.1f}분")
    print(f"   ─────────────────────")
    print(f"   총계:      {total_hours:.1f}시간 ({total_minutes:.0f}분)")
    
    print()
    print("="*80)
    print("🎯 실행 방법")
    print("="*80)
    print("""
각 단계를 순차적으로 실행하세요:

# 1단계: 번역
python scripts/translate_all_content.py

# 2단계: 분류  
python scripts/classify_with_solar.py

# 3단계: 피싱 타입
python scripts/classify_phishing_type_solar.py

# 4단계: 임베딩
python scripts/embed_with_bge.py

# 중복 제거 (선택)
python scripts/deduplicate_data.py

또는 한번에 실행:
python scripts/run_full_pipeline_ollama.py
""")
    
    print("\n✅ 상태 확인 완료!\n")

if __name__ == '__main__':
    main()
