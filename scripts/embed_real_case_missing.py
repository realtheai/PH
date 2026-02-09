#!/usr/bin/env python3
"""
REAL_CASE 중 임베딩이 없는 이미지 처리
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

def embed_real_case_images():
    """REAL_CASE 이미지 중 임베딩이 없는 것만 처리"""
    print("\n" + "="*100)
    print("🔴 REAL_CASE 이미지 임베딩 처리 (BGE-M3)")
    print("="*100 + "\n")
    
    # REAL_CASE이면서 embedding이 없는 이미지 가져오기
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/phishing_images",
        headers=HEADERS,
        params={
            'select': 'id,ocr_text,translated_content,translated_text,local_path',
            'classification': 'eq.REAL_CASE',
            'embedding': 'is.null',
            'limit': 1000
        }
    )
    
    if response.status_code != 200:
        print(f"❌ 이미지 조회 실패: {response.status_code}")
        print(f"   응답: {response.text}")
        return
    
    images_list = response.json()
    total = len(images_list)
    
    if total == 0:
        print("✅ 임베딩할 REAL_CASE 이미지가 없습니다!")
        print("   모든 데이터가 벡터화 완료되었습니다! 🎉")
        return
    
    print(f"📊 총 {total}개 REAL_CASE 이미지 임베딩 시작...\n")
    
    success = 0
    failed = 0
    no_text = 0
    
    for i, img in enumerate(images_list, 1):
        # 텍스트 우선순위: translated_content > translated_text > ocr_text
        text = img.get('translated_content') or img.get('translated_text') or img.get('ocr_text', '')
        
        if not text or len(text.strip()) < 5:
            print(f"[{i}/{total}] ID {img['id']}: ⚠️ 텍스트 없음 또는 너무 짧음")
            no_text += 1
            failed += 1
            continue
        
        # 임베딩 생성
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
                if i % 10 == 0 or i == total:
                    print(f"[{i}/{total}] ✅ 진행률: {i/total*100:.1f}% (성공: {success}, 실패: {failed})")
            else:
                failed += 1
                print(f"[{i}/{total}] ID {img['id']}: ❌ DB 업데이트 실패 ({update_resp.status_code})")
        else:
            failed += 1
            print(f"[{i}/{total}] ID {img['id']}: ❌ 임베딩 생성 실패")
        
        time.sleep(0.1)  # API 부하 방지
    
    print()
    print("="*100)
    print(f"✅ REAL_CASE 이미지 임베딩 완료!")
    print("="*100)
    print(f"   총 처리: {total}개")
    print(f"   ✅ 성공: {success}개")
    print(f"   ❌ 실패: {failed}개")
    print(f"      - 텍스트 없음: {no_text}개")
    print(f"      - 기타 오류: {failed - no_text}개")
    print(f"   📈 성공률: {success/total*100:.1f}%" if total > 0 else "")
    print("="*100 + "\n")

if __name__ == '__main__':
    print("\n🚀 REAL_CASE 미벡터화 이미지 처리 시작\n")
    
    # Ollama BGE-M3 모델 확인
    print("🔍 BGE-M3 모델 확인 중...")
    try:
        check = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": "bge-m3:567m", "prompt": "test"},
            timeout=5
        )
        if check.status_code == 200:
            print("✅ BGE-M3 모델 준비 완료\n")
        else:
            print(f"⚠️ BGE-M3 모델 응답 이상: {check.status_code}\n")
    except Exception as e:
        print(f"❌ Ollama 연결 실패: {str(e)}")
        print("   Ollama가 실행 중인지 확인해주세요.\n")
        exit(1)
    
    embed_real_case_images()
    print("✅ 전체 처리 완료!\n")
