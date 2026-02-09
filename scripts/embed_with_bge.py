#!/usr/bin/env python3
"""
BGE-M3 모델로 임베딩 생성
"""
import requests
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

HEADERS = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

def get_embedding(text):
    """BGE-M3로 임베딩 생성"""
    try:
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={
                "model": "bge-m3:567m",
                "prompt": text[:1000]  # 최대 1000자
            },
            timeout=30
        )
        
        if response.status_code == 200:
            embedding = response.json()['embedding']
            
            # 1536 차원으로 패딩/자르기
            if len(embedding) < 1536:
                embedding = embedding + [0.0] * (1536 - len(embedding))
            elif len(embedding) > 1536:
                embedding = embedding[:1536]
            
            return embedding
        else:
            return None
    except Exception as e:
        print(f"   ❌ 임베딩 오류: {str(e)[:50]}")
        return None

def embed_news():
    """뉴스 임베딩"""
    print("\n" + "="*80)
    print("📰 뉴스 임베딩 (BGE-M3)")
    print("="*80 + "\n")
    
    # embedding이 없는 뉴스 가져오기
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/phishing_news",
        headers=HEADERS,
        params={
            'select': 'id,title,content,translated_content',
            'embedding': 'is.null',
            'limit': 1000
        }
    )
    
    if response.status_code != 200:
        print(f"❌ 뉴스 조회 실패: {response.status_code}")
        return
    
    news_list = response.json()
    total = len(news_list)
    
    if total == 0:
        print("✅ 임베딩할 뉴스가 없습니다!")
        return
    
    print(f"📊 총 {total}개 뉴스 임베딩 시작...\n")
    
    success = 0
    failed = 0
    
    for i, news in enumerate(news_list, 1):
        text = news.get('translated_content') or news.get('content') or news.get('title', '')
        
        if not text:
            print(f"[{i}/{total}] ID {news['id']}: ⚠️ 텍스트 없음")
            failed += 1
            continue
        
        embedding = get_embedding(text)
        
        if embedding:
            # Supabase 업데이트
            update_resp = requests.patch(
                f"{SUPABASE_URL}/rest/v1/phishing_news",
                headers=HEADERS,
                params={'id': f"eq.{news['id']}"},
                json={'embedding': embedding}
            )
            
            if update_resp.status_code in [200, 204]:
                success += 1
                print(f"[{i}/{total}] ID {news['id']}: ✅")
            else:
                failed += 1
                print(f"[{i}/{total}] ID {news['id']}: ❌ 업데이트 실패")
        else:
            failed += 1
            print(f"[{i}/{total}] ID {news['id']}: ❌ 임베딩 실패")
        
        time.sleep(0.05)
    
    print()
    print("="*80)
    print(f"✅ 뉴스 임베딩 완료!")
    print(f"   성공: {success}개")
    print(f"   실패: {failed}개")
    print("="*80)

def embed_images():
    """이미지 임베딩"""
    print("\n" + "="*80)
    print("🖼️ 이미지 임베딩 (BGE-M3)")
    print("="*80 + "\n")
    
    # embedding이 없는 이미지 가져오기
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/phishing_images",
        headers=HEADERS,
        params={
            'select': 'id,ocr_text,translated_content',
            'embedding': 'is.null',
            'limit': 1000
        }
    )
    
    if response.status_code != 200:
        print(f"❌ 이미지 조회 실패: {response.status_code}")
        return
    
    images_list = response.json()
    total = len(images_list)
    
    if total == 0:
        print("✅ 임베딩할 이미지가 없습니다!")
        return
    
    print(f"📊 총 {total}개 이미지 임베딩 시작...\n")
    
    success = 0
    failed = 0
    
    for i, img in enumerate(images_list, 1):
        text = img.get('translated_content') or img.get('ocr_text', '')
        
        if not text:
            print(f"[{i}/{total}] ID {img['id']}: ⚠️ 텍스트 없음")
            failed += 1
            continue
        
        embedding = get_embedding(text)
        
        if embedding:
            # Supabase 업데이트
            update_resp = requests.patch(
                f"{SUPABASE_URL}/rest/v1/phishing_images",
                headers=HEADERS,
                params={'id': f"eq.{img['id']}"},
                json={'embedding': embedding}
            )
            
            if update_resp.status_code in [200, 204]:
                success += 1
                if i % 10 == 0:
                    print(f"[{i}/{total}] ✅ 진행률: {i/total*100:.1f}%")
            else:
                failed += 1
                print(f"[{i}/{total}] ID {img['id']}: ❌ 업데이트 실패")
        else:
            failed += 1
            print(f"[{i}/{total}] ID {img['id']}: ❌ 임베딩 실패")
        
        time.sleep(0.05)
    
    print()
    print("="*80)
    print(f"✅ 이미지 임베딩 완료!")
    print(f"   성공: {success}개")
    print(f"   실패: {failed}개")
    print("="*80)

if __name__ == '__main__':
    print("\n🚀 BGE-M3 임베딩 시작")
    embed_news()
    embed_images()
    print("\n✅ 전체 임베딩 완료!\n")
