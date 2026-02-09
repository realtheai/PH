#!/usr/bin/env python3
"""
OpenAI 임베딩으로 DB 데이터 재생성
"""
import os
import requests
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

headers = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

def create_openai_embedding(text: str) -> list:
    """OpenAI로 임베딩 생성"""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000],
            encoding_format="float"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"   ❌ 임베딩 오류: {str(e)[:50]}")
        return None

def reembed_images():
    """이미지 REAL_CASE 재임베딩"""
    print("\n" + "="*100)
    print("🖼️  이미지 REAL_CASE 재임베딩 (OpenAI)")
    print("="*100 + "\n")
    
    # REAL_CASE 이미지 조회
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/phishing_images",
        headers=headers,
        params={
            'select': 'id,ocr_text,translated_content,translated_text',
            'classification': 'eq.REAL_CASE',
            'limit': 500
        },
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ 데이터 조회 실패: {response.status_code}")
        return
    
    images = response.json()
    total = len(images)
    
    print(f"📊 총 {total}개 이미지 재임베딩 시작...\n")
    
    success = 0
    failed = 0
    
    for i, img in enumerate(images, 1):
        # 텍스트 우선순위
        text = img.get('translated_content') or img.get('translated_text') or img.get('ocr_text', '')
        
        if not text or len(text.strip()) < 5:
            failed += 1
            continue
        
        # OpenAI 임베딩 생성
        embedding = create_openai_embedding(text)
        
        if embedding and len(embedding) == 1536:
            # DB 업데이트
            update_resp = requests.patch(
                f"{SUPABASE_URL}/rest/v1/phishing_images",
                headers=headers,
                params={'id': f"eq.{img['id']}"},
                json={'embedding': embedding}
            )
            
            if update_resp.status_code in [200, 204]:
                success += 1
                if i % 50 == 0 or i == total:
                    print(f"[{i}/{total}] ✅ 진행률: {i/total*100:.1f}% (성공: {success}, 실패: {failed})")
            else:
                failed += 1
        else:
            failed += 1
        
        # Rate limit 방지
        time.sleep(0.05)
    
    print()
    print(f"✅ 이미지 재임베딩 완료: 성공 {success}개, 실패 {failed}개")
    return success, failed

def reembed_news():
    """뉴스 REAL_CASE 재임베딩"""
    print("\n" + "="*100)
    print("📰 뉴스 REAL_CASE 재임베딩 (OpenAI)")
    print("="*100 + "\n")
    
    # REAL_CASE 뉴스 조회
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/phishing_news",
        headers=headers,
        params={
            'select': 'id,title,content,translated_content',
            'category': 'eq.REAL_CASE',
            'limit': 2000
        },
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ 데이터 조회 실패: {response.status_code}")
        return
    
    news_list = response.json()
    total = len(news_list)
    
    print(f"📊 총 {total}개 뉴스 재임베딩 시작...\n")
    
    success = 0
    failed = 0
    
    for i, news in enumerate(news_list, 1):
        # 텍스트 우선순위
        text = news.get('translated_content') or news.get('content') or news.get('title', '')
        
        if not text or len(text.strip()) < 5:
            failed += 1
            continue
        
        # OpenAI 임베딩 생성
        embedding = create_openai_embedding(text)
        
        if embedding and len(embedding) == 1536:
            # DB 업데이트
            update_resp = requests.patch(
                f"{SUPABASE_URL}/rest/v1/phishing_news",
                headers=headers,
                params={'id': f"eq.{news['id']}"},
                json={'embedding': embedding}
            )
            
            if update_resp.status_code in [200, 204]:
                success += 1
                if i % 100 == 0 or i == total:
                    print(f"[{i}/{total}] ✅ 진행률: {i/total*100:.1f}% (성공: {success}, 실패: {failed})")
            else:
                failed += 1
        else:
            failed += 1
        
        # Rate limit 방지
        time.sleep(0.05)
    
    print()
    print(f"✅ 뉴스 재임베딩 완료: 성공 {success}개, 실패 {failed}개")
    return success, failed

if __name__ == '__main__':
    print("\n" + "="*100)
    print("🚀 OpenAI 임베딩 전환 시작")
    print("="*100)
    print()
    print("📋 작업 내용:")
    print("   1. 모든 REAL_CASE 데이터의 임베딩을 OpenAI로 재생성")
    print("   2. BGE-M3 (Ollama) → OpenAI text-embedding-3-small")
    print("   3. 약 1,373개 데이터 처리 예상")
    print()
    print("💰 예상 비용: ~$0.003 (약 3원)")
    print("⏱️  예상 시간: 10-15분")
    print()
    print("="*100 + "\n")
    
    input("계속하려면 Enter를 누르세요...")
    
    start_time = time.time()
    
    # 이미지 재임베딩
    img_success, img_failed = reembed_images()
    
    # 뉴스 재임베딩
    news_success, news_failed = reembed_news()
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*100)
    print("✅ 전체 재임베딩 완료!")
    print("="*100)
    print(f"   이미지: 성공 {img_success}개, 실패 {img_failed}개")
    print(f"   뉴스: 성공 {news_success}개, 실패 {news_failed}개")
    print(f"   총 성공: {img_success + news_success}개")
    print(f"   소요 시간: {elapsed/60:.1f}분")
    print("="*100 + "\n")
    
    print("🎉 이제 GitHub Actions 배포 가능합니다!")
    print("   - Ollama 서버 불필요")
    print("   - OpenAI API 키만 필요")
    print("   - 벡터 검색 정상 작동\n")
