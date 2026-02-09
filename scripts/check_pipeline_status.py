#!/usr/bin/env python3
"""
파이프라인 진행 상황 확인 스크립트
"""
import os
import requests
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

# Supabase 설정
SUPABASE_URL = os.getenv('SUPABASE_URL')
# SERVICE_ROLE_KEY 사용 (RLS 우회)
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ANON_KEY')
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

def get_count(table: str, filter_query: str = "") -> int:
    """Supabase에서 카운트 조회"""
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*&{filter_query}"
    headers_with_count = {**HEADERS, 'Prefer': 'count=exact'}
    response = requests.get(url, headers=headers_with_count)
    if response.status_code == 200:
        return int(response.headers.get('Content-Range', '0-0/0').split('/')[-1])
    return 0

def get_data(table: str, columns: str, filter_query: str = "", limit: int = 10000) -> list:
    """Supabase에서 데이터 조회"""
    url = f"{SUPABASE_URL}/rest/v1/{table}?select={columns}&{filter_query}&limit={limit}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return []

def check_status():
    """각 테이블별 진행 상황 확인"""
    
    print("\n" + "="*70)
    print("📊 파이프라인 진행 상황 체크")
    print("="*70 + "\n")
    
    # 1. 뉴스 데이터 확인
    print("1️⃣  뉴스 데이터 (phishing_news)")
    print("-" * 70)
    
    # 전체 뉴스 수
    total_news = get_count('phishing_news')
    print(f"   📰 전체 뉴스: {total_news:,}개")
    
    # 번역 완료된 뉴스 (translated_content가 있는 경우)
    translated_news_count = get_count('phishing_news', 'translated_content=not.is.null')
    print(f"   🌐 번역 완료: {translated_news_count:,}개")
    
    # 분류 완료된 뉴스
    classified_news_count = get_count('phishing_news', 'classification=not.is.null')
    print(f"   🏷️  분류 완료: {classified_news_count:,}개")
    
    # 분류별 카운트
    if classified_news_count > 0:
        all_classified = get_data('phishing_news', 'classification', 'classification=not.is.null')
        classifications = Counter([item['classification'] for item in all_classified])
        print(f"      - REAL_CASE: {classifications.get('REAL_CASE', 0):,}개")
        print(f"      - NEWS: {classifications.get('NEWS', 0):,}개")
        print(f"      - NOISE: {classifications.get('NOISE', 0):,}개")
    
    # phishing_type 할당된 뉴스
    typed_news_count = get_count('phishing_news', 'phishing_type=not.is.null')
    print(f"   🎯 피싱 타입 할당: {typed_news_count:,}개")
    
    # 임베딩 생성된 뉴스
    embedded_news_count = get_count('phishing_news', 'embedding=not.is.null')
    print(f"   🧮 임베딩 생성: {embedded_news_count:,}개")
    
    print()
    
    # 2. 이미지 데이터 확인
    print("2️⃣  이미지 데이터 (phishing_images)")
    print("-" * 70)
    
    # 전체 이미지 수
    total_images = get_count('phishing_images')
    print(f"   🖼️  전체 이미지: {total_images:,}개")
    
    # OCR 완료된 이미지
    ocr_images_count = get_count('phishing_images', 'ocr_text=not.is.null')
    print(f"   📝 OCR 완료: {ocr_images_count:,}개")
    
    # 번역 완료된 이미지
    translated_images_count = get_count('phishing_images', 'translated_content=not.is.null')
    print(f"   🌐 번역 완료: {translated_images_count:,}개")
    
    # 분류 완료된 이미지
    classified_images_count = get_count('phishing_images', 'classification=not.is.null')
    print(f"   🏷️  분류 완료: {classified_images_count:,}개")
    
    # 분류별 카운트
    if classified_images_count > 0:
        all_classified_img = get_data('phishing_images', 'classification', 'classification=not.is.null')
        img_classifications = Counter([item['classification'] for item in all_classified_img])
        print(f"      - REAL_CASE: {img_classifications.get('REAL_CASE', 0):,}개")
        print(f"      - NEWS: {img_classifications.get('NEWS', 0):,}개")
        print(f"      - NOISE: {img_classifications.get('NOISE', 0):,}개")
    
    # phishing_type 할당된 이미지
    typed_images_count = get_count('phishing_images', 'phishing_type=not.is.null')
    print(f"   🎯 피싱 타입 할당: {typed_images_count:,}개")
    
    # 임베딩 생성된 이미지
    embedded_images_count = get_count('phishing_images', 'embedding=not.is.null')
    print(f"   🧮 임베딩 생성: {embedded_images_count:,}개")
    
    print()
    
    # 3. Reddit 데이터 확인
    print("3️⃣  Reddit 데이터 (phishing_reddit)")
    print("-" * 70)
    
    total_reddit = get_count('phishing_reddit')
    print(f"   💬 전체 Reddit 게시물: {total_reddit:,}개")
    
    # 번역 완료된 Reddit
    translated_reddit_count = get_count('phishing_reddit', 'translated_content=not.is.null')
    print(f"   🌐 번역 완료: {translated_reddit_count:,}개")
    
    # 분류 완료된 Reddit
    classified_reddit_count = get_count('phishing_reddit', 'classification=not.is.null')
    print(f"   🏷️  분류 완료: {classified_reddit_count:,}개")
    
    # 임베딩 생성된 Reddit
    embedded_reddit_count = get_count('phishing_reddit', 'embedding=not.is.null')
    print(f"   🧮 임베딩 생성: {embedded_reddit_count:,}개")
    
    print()
    
    # 4. 전체 요약
    print("="*70)
    print("📈 전체 요약")
    print("="*70)
    
    total_all = total_news + total_images + total_reddit
    total_translated = translated_news_count + translated_images_count + translated_reddit_count
    total_classified = classified_news_count + classified_images_count + classified_reddit_count
    total_typed = typed_news_count + typed_images_count
    total_embedded = embedded_news_count + embedded_images_count + embedded_reddit_count
    
    print(f"   전체 데이터: {total_all:,}개")
    if total_all > 0:
        print(f"   번역 완료: {total_translated:,}개 ({total_translated/total_all*100:.1f}%)")
        print(f"   분류 완료: {total_classified:,}개 ({total_classified/total_all*100:.1f}%)")
        print(f"   타입 할당: {total_typed:,}개")
        print(f"   임베딩 생성: {total_embedded:,}개 ({total_embedded/total_all*100:.1f}%)")
    
    print()
    
    # 5. 다음 단계 추천
    print("="*70)
    print("💡 다음 단계 추천")
    print("="*70)
    
    if total_all > 0:
        if total_translated < total_all:
            missing_translation = total_all - total_translated
            print(f"   ⚠️  번역 필요: {missing_translation:,}개 항목")
            print(f"      → python scripts/translate_all_content.py 실행 필요")
        
        if total_classified < total_all:
            missing_classification = total_all - total_classified
            print(f"   ⚠️  분류 필요: {missing_classification:,}개 항목")
            print(f"      → python scripts/classify_data.py 실행 필요")
        
        if total_typed == 0 and classified_news_count > 0:
            print(f"   ⚠️  피싱 타입 할당 필요")
            print(f"      → python scripts/classify_phishing_type.py 실행 필요")
        
        if total_embedded < total_all:
            missing_embedding = total_all - total_embedded
            print(f"   ⚠️  임베딩 생성 필요: {missing_embedding:,}개 항목")
            print(f"      → python scripts/run_full_embedding_openai.py 실행 필요")
        
        if total_translated == total_all and total_classified == total_all and total_embedded == total_all:
            print(f"   ✅ 모든 단계 완료!")
            print(f"      → 중복 제거 실행: python scripts/deduplicate_data.py")
    else:
        print(f"   ⚠️  데이터가 없습니다!")
        print(f"      → 크롤링 스크립트를 먼저 실행하세요.")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        check_status()
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
