#!/usr/bin/env python3
"""
누락된 처리 단계 자동 실행
1. 상태 확인
2. 번역 필요 시 실행
3. 분류 필요 시 실행
4. 피싱타입 필요 시 실행
5. 임베딩 필요 시 실행
"""
import os
import sys
import requests
from dotenv import load_dotenv

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
    except Exception as e:
        print(f"❌ 에러: {e}")
    return 0

def check_processing_status():
    """처리 상태 확인"""
    print("\n" + "="*80)
    print("🔍 데이터 처리 상태 확인")
    print("="*80 + "\n")
    
    status = {}
    
    # phishing_news 상태
    print("📰 phishing_news 테이블")
    print("-" * 80)
    status['news_total'] = get_count('phishing_news')
    status['news_translated'] = get_count('phishing_news', 'translated_content=not.is.null')
    status['news_classified'] = get_count('phishing_news', 'classification=not.is.null')
    status['news_typed'] = get_count('phishing_news', 'phishing_type=not.is.null')
    status['news_embedded'] = get_count('phishing_news', 'embedding=not.is.null')
    
    print(f"   전체: {status['news_total']:,}개")
    print(f"   번역: {status['news_translated']:,}개 ({status['news_translated']/max(status['news_total'],1)*100:.1f}%)")
    print(f"   분류: {status['news_classified']:,}개 ({status['news_classified']/max(status['news_total'],1)*100:.1f}%)")
    print(f"   타입: {status['news_typed']:,}개 ({status['news_typed']/max(status['news_total'],1)*100:.1f}%)")
    print(f"   임베딩: {status['news_embedded']:,}개 ({status['news_embedded']/max(status['news_total'],1)*100:.1f}%)")
    print()
    
    # phishing_images 상태
    print("🖼️  phishing_images 테이블")
    print("-" * 80)
    status['images_total'] = get_count('phishing_images')
    status['images_ocr'] = get_count('phishing_images', 'ocr_text=not.is.null')
    status['images_translated'] = get_count('phishing_images', 'translated_content=not.is.null')
    status['images_classified'] = get_count('phishing_images', 'classification=not.is.null')
    status['images_typed'] = get_count('phishing_images', 'phishing_type=not.is.null')
    status['images_embedded'] = get_count('phishing_images', 'embedding=not.is.null')
    
    print(f"   전체: {status['images_total']:,}개")
    print(f"   OCR: {status['images_ocr']:,}개 ({status['images_ocr']/max(status['images_total'],1)*100:.1f}%)")
    print(f"   번역: {status['images_translated']:,}개 ({status['images_translated']/max(status['images_total'],1)*100:.1f}%)")
    print(f"   분류: {status['images_classified']:,}개 ({status['images_classified']/max(status['images_total'],1)*100:.1f}%)")
    print(f"   타입: {status['images_typed']:,}개 ({status['images_typed']/max(status['images_total'],1)*100:.1f}%)")
    print(f"   임베딩: {status['images_embedded']:,}개 ({status['images_embedded']/max(status['images_total'],1)*100:.1f}%)")
    print()
    
    return status

def run_missing_steps(status):
    """누락된 단계 실행"""
    print("="*80)
    print("⚙️  누락된 처리 단계 실행")
    print("="*80 + "\n")
    
    total = status['news_total'] + status['images_total']
    
    if total == 0:
        print("❌ 데이터가 없습니다!")
        return
    
    steps_to_run = []
    
    # 번역 필요 여부
    if status['news_translated'] < status['news_total'] or status['images_translated'] < status['images_total']:
        steps_to_run.append(('번역', 'translate_all_content.py'))
    
    # 분류 필요 여부
    if status['news_classified'] < status['news_total'] or status['images_classified'] < status['images_total']:
        steps_to_run.append(('분류', 'classify_data.py'))
    
    # 피싱타입 필요 여부
    if status['news_typed'] < status['news_classified']:
        steps_to_run.append(('피싱타입', 'classify_phishing_type.py'))
    
    # 임베딩 필요 여부
    if status['news_embedded'] < status['news_total'] or status['images_embedded'] < status['images_total']:
        steps_to_run.append(('임베딩', 'run_full_embedding_openai.py'))
    
    if not steps_to_run:
        print("✅ 모든 처리가 완료되었습니다!")
        return
    
    print(f"📋 실행할 단계 ({len(steps_to_run)}개):")
    for i, (name, script) in enumerate(steps_to_run, 1):
        print(f"   {i}. {name}: {script}")
    print()
    
    # 실행 확인
    response = input("실행하시겠습니까? (y/n): ")
    if response.lower() != 'y':
        print("취소되었습니다.")
        return
    
    print()
    
    # 순차 실행
    for name, script in steps_to_run:
        print("="*80)
        print(f"▶️  {name} 실행 중... ({script})")
        print("="*80)
        
        import subprocess
        result = subprocess.run(
            ['python', f'scripts/{script}'],
            cwd='/home/realtheai/phishingapp'
        )
        
        if result.returncode != 0:
            print(f"\n❌ {name} 실행 실패!")
            response = input("계속하시겠습니까? (y/n): ")
            if response.lower() != 'y':
                break
        else:
            print(f"\n✅ {name} 완료!")
        print()

if __name__ == "__main__":
    try:
        status = check_processing_status()
        
        if status['news_total'] == 0 and status['images_total'] == 0:
            print("\n" + "="*80)
            print("⚠️  RLS 정책이 아직 수정되지 않았거나, 데이터 접근 권한이 없습니다.")
            print("="*80)
            print("\nSupabase SQL Editor에서 RLS 정책 수정 SQL을 실행해주세요.")
            print("SQL 파일: fix_rls_policies.sql")
            sys.exit(1)
        
        run_missing_steps(status)
        
        print("\n" + "="*80)
        print("✅ 처리 완료!")
        print("="*80 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
