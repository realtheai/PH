"""
전체 임베딩 생성 (OpenAI 버전 - GitHub Actions용)
"""
import os
import time
import requests
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}


def create_embedding(text: str, retry=3) -> List[float]:
    """OpenAI text-embedding-3-small로 임베딩 생성"""
    text = text[:8000]  # OpenAI는 더 긴 텍스트 지원
    
    for attempt in range(retry):
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                encoding_format="float"
            )
            embedding = response.data[0].embedding
            
            # 1536 차원으로 맞추기
            if len(embedding) < 1536:
                embedding = embedding + [0.0] * (1536 - len(embedding))
            elif len(embedding) > 1536:
                embedding = embedding[:1536]
            
            return embedding
        except Exception as e:
            print(f"❌ 임베딩 실패 (attempt {attempt+1}): {str(e)[:50]}")
            time.sleep(2 ** attempt)  # Exponential backoff
            if attempt == retry - 1:
                return None
    return None


def get_records_without_embedding(limit=1000) -> List[Dict]:
    """임베딩이 없는 레코드 조회"""
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
    """임베딩 업데이트"""
    url = f"{SUPABASE_URL}/rest/v1/phishing_news"
    params = {'id': f'eq.{record_id}'}
    data = {'embedding': embedding}
    try:
        response = requests.patch(url, headers=HEADERS, params=params, json=data, timeout=30)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ 업데이트 실패: {e}")
        return False


def main():
    print("=" * 60)
    print("🧠 OpenAI 임베딩 생성 (GitHub Actions)")
    print("=" * 60)
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY가 없습니다!")
        return
    
    total_success = 0
    total_fail = 0
    round_num = 0
    
    while True:
        round_num += 1
        
        # 레코드 조회 (1000건씩)
        records = get_records_without_embedding(limit=1000)
        
        if not records:
            print("\n🎉 모든 레코드 처리 완료!")
            break
        
        batch_total = len(records)
        print(f"\n🚀 라운드 {round_num}: {batch_total}건 처리 시작...")
        
        # 배치 처리
        for i, record in enumerate(records, 1):
            record_id = record['id']
            title = record.get('title', '')
            content = record.get('content', '')
            text = f"{title} {content}"
            
            # 진행 상황 (10개마다)
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
            
            time.sleep(0.2)  # Rate limiting
        
        print(f"\n  라운드 {round_num} 완료: 성공 {total_success}, 실패 {total_fail}")
    
    # 최종 결과
    print("\n" + "=" * 60)
    print("🎉 전체 완료!")
    print("=" * 60)
    print(f"✅ 총 성공: {total_success}건")
    print(f"❌ 총 실패: {total_fail}건")


if __name__ == "__main__":
    main()
