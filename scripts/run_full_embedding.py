"""
전체 임베딩 생성 (자동 실행 버전)
"""
import os
import time
import requests
from typing import List, Dict
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
GEMINI_API_KEYS = [
    os.getenv('GEMINI_API_KEY'),
    os.getenv('GEMINI_API_KEY_2'),
    os.getenv('GEMINI_API_KEY_3'),
    os.getenv('GEMINI_API_KEY_4'),
    os.getenv('GEMINI_API_KEY_5'),
    os.getenv('GEMINI_API_KEY_6'),
]

current_key_index = 0

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}


def get_gemini_client():
    global current_key_index
    api_key = GEMINI_API_KEYS[current_key_index]
    if not api_key:
        current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
        api_key = GEMINI_API_KEYS[current_key_index]
    genai.configure(api_key=api_key)


def create_embedding(text: str, retry=3) -> List[float]:
    global current_key_index
    text = text[:5000]
    
    for attempt in range(retry):
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            embedding = result['embedding']
            if len(embedding) < 1536:
                embedding = embedding + [0.0] * (1536 - len(embedding))
            elif len(embedding) > 1536:
                embedding = embedding[:1536]
            return embedding
        except Exception as e:
            current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
            genai.configure(api_key=GEMINI_API_KEYS[current_key_index])
            time.sleep(1)
            if attempt == retry - 1:
                print(f"❌ 임베딩 실패: {str(e)[:50]}")
                return None
    return None


def get_records_without_embedding(limit=1000) -> List[Dict]:
    url = f"{SUPABASE_URL}/rest/v1/phishing_news"
    params = {
        'select': 'id,title,content',
        'embedding': 'is.null',
        'order': 'id.asc',
        'limit': limit
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ 조회 실패: {e}")
        return []


def update_embedding(record_id: int, embedding: List[float]) -> bool:
    url = f"{SUPABASE_URL}/rest/v1/phishing_news"
    params = {'id': f'eq.{record_id}'}
    data = {'embedding': embedding}
    try:
        response = requests.patch(url, headers=HEADERS, params=params, json=data, timeout=30)
        response.raise_for_status()
        return True
    except:
        return False


def get_stats() -> Dict:
    url = f"{SUPABASE_URL}/rest/v1/phishing_embedding_stats"
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data[0] if data else {}
    except:
        return {}


def main():
    print("=" * 60)
    print("전체 임베딩 생성 (자동 모드)")
    print("=" * 60)
    
    get_gemini_client()
    
    total_success = 0
    total_fail = 0
    round_num = 0
    
    while True:
        round_num += 1
        
        # 통계 확인
        stats = get_stats()
        if stats:
            print(f"\n📊 현재 상태 (라운드 {round_num}):")
            print(f"   총 레코드: {stats.get('total_records', 0)}건")
            print(f"   임베딩 완료: {stats.get('embedded_records', 0)}건 ({stats.get('completion_percentage', 0)}%)")
            print(f"   대기 중: {stats.get('pending_records', 0)}건")
        
        # 레코드 조회 (1000건씩)
        records = get_records_without_embedding(limit=1000)
        
        if not records:
            print("\n🎉 모든 레코드 처리 완료!")
            break
        
        batch_total = len(records)
        print(f"\n🚀 {batch_total}건 처리 시작...")
        
        # 배치 처리
        for i, record in enumerate(records, 1):
            record_id = record['id']
            title = record.get('title', '')
            content = record.get('content', '')
            text = f"{title} {content}"
            
            # 진행 상황
            if i % 10 == 0 or i == batch_total:
                preview = title[:30] + "..." if len(title) > 30 else title
                print(f"  [{i}/{batch_total}] {preview}", end=' ')
            
            # 임베딩 생성 & 업데이트
            embedding = create_embedding(text)
            if embedding and update_embedding(record_id, embedding):
                total_success += 1
                if i % 10 == 0 or i == batch_total:
                    print("✅")
            else:
                total_fail += 1
                if i % 10 == 0 or i == batch_total:
                    print("❌")
            
            time.sleep(0.5)
        
        print(f"\n  라운드 {round_num} 완료: 성공 {total_success}, 실패 {total_fail}")
    
    # 최종 결과
    print("\n" + "=" * 60)
    print("🎉 전체 완료!")
    print("=" * 60)
    print(f"✅ 총 성공: {total_success}건")
    print(f"❌ 총 실패: {total_fail}건")
    
    stats = get_stats()
    if stats:
        print(f"\n📊 최종 통계:")
        print(f"   임베딩 완료: {stats.get('embedded_records', 0)}건 ({stats.get('completion_percentage', 0)}%)")


if __name__ == "__main__":
    main()
