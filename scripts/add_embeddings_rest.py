"""
기존 Supabase 데이터에 임베딩 추가 (REST API 사용)
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

# REST API 헤더
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}


def get_gemini_client():
    """Gemini API 초기화"""
    global current_key_index
    api_key = GEMINI_API_KEYS[current_key_index]
    if not api_key:
        current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
        api_key = GEMINI_API_KEYS[current_key_index]
    genai.configure(api_key=api_key)


def create_embedding(text: str, retry=3) -> List[float]:
    """텍스트를 임베딩 벡터로 변환"""
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
            
            # 1536차원으로 패딩
            if len(embedding) < 1536:
                embedding = embedding + [0.0] * (1536 - len(embedding))
            elif len(embedding) > 1536:
                embedding = embedding[:1536]
            
            return embedding
            
        except Exception as e:
            # API 키 로테이션
            current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
            genai.configure(api_key=GEMINI_API_KEYS[current_key_index])
            
            time.sleep(1)
            
            if attempt == retry - 1:
                print(f"❌ 임베딩 실패: {str(e)[:50]}")
                return None
    
    return None


def get_records_without_embedding(limit=100) -> List[Dict]:
    """embedding이 NULL인 레코드 조회"""
    
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
        print(f"❌ 레코드 조회 실패: {e}")
        return []


def update_embedding(record_id: int, embedding: List[float]) -> bool:
    """레코드에 임베딩 업데이트"""
    
    url = f"{SUPABASE_URL}/rest/v1/phishing_news"
    params = {'id': f'eq.{record_id}'}
    data = {'embedding': embedding}
    
    try:
        response = requests.patch(url, headers=HEADERS, params=params, json=data, timeout=30)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ 업데이트 실패 (ID {record_id}): {e}")
        return False


def get_stats() -> Dict:
    """통계 조회"""
    
    url = f"{SUPABASE_URL}/rest/v1/phishing_embedding_stats"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data[0] if data else {}
    except Exception as e:
        print(f"⚠️  통계 조회 실패: {e}")
        return {}


def process_batch(batch: List[Dict]) -> tuple:
    """배치 처리"""
    
    success = 0
    fail = 0
    
    for record in batch:
        record_id = record['id']
        title = record.get('title', '')
        content = record.get('content', '')
        
        # 텍스트 결합
        text = f"{title} {content}"
        
        # 미리보기
        preview = title[:40] + "..." if len(title) > 40 else title
        print(f"  [{record_id}] {preview}", end=' ')
        
        # 임베딩 생성
        embedding = create_embedding(text)
        
        if embedding:
            # 업데이트
            if update_embedding(record_id, embedding):
                success += 1
                print("✅")
            else:
                fail += 1
                print("❌")
        else:
            fail += 1
            print("❌")
        
        # Rate limit
        time.sleep(0.5)
    
    return success, fail


def main():
    """메인 실행"""
    
    print("=" * 60)
    print("기존 Supabase 데이터에 임베딩 추가 (REST API)")
    print("=" * 60)
    
    get_gemini_client()
    
    # 1. 통계 확인
    print("\n📊 현재 상태:")
    stats = get_stats()
    if stats:
        print(f"   총 레코드: {stats.get('total_records', 0)}건")
        print(f"   임베딩 완료: {stats.get('embedded_records', 0)}건")
        print(f"   대기 중: {stats.get('pending_records', 0)}건")
        print(f"   완료율: {stats.get('completion_percentage', 0)}%")
    
    # 2. 모드 선택 (인자로 받기)
    import sys
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("\n🧪 모드 선택:")
        print("1. 테스트 (100건만)")
        print("2. 전체 (1000건)")
        print("3. 전체 (모든 레코드)")
        choice = input("\n선택 (1/2/3): ").strip()
    
    if choice == '1':
        max_records = 100
        print("✅ 테스트 모드: 100건")
        auto_confirm = True
    elif choice == '2':
        max_records = 1000
        print("✅ 중간 모드: 1000건")
        auto_confirm = False
    else:
        max_records = 10000  # 충분히 큰 수
        print("✅ 전체 모드")
        auto_confirm = False
    
    # 3. 레코드 조회
    print(f"\n📥 임베딩 대기 중인 레코드 조회 (최대 {max_records}건)...")
    records = get_records_without_embedding(limit=max_records)
    
    if not records:
        print("✅ 모든 레코드에 임베딩이 이미 있습니다!")
        return
    
    total = len(records)
    print(f"   조회됨: {total}건")
    
    # 예상 시간
    estimated_time = total * 0.5 / 60
    print(f"   예상 시간: {estimated_time:.1f}분")
    
    # 확인
    if total > 100 and not auto_confirm:
        try:
            response = input("\n계속 진행하시겠습니까? (y/n): ")
            if response.lower() != 'y':
                print("취소됨")
                return
        except EOFError:
            print("\n✅ 자동 진행 (백그라운드 모드)")
            pass
    
    # 4. 배치 처리
    print(f"\n🚀 임베딩 생성 시작")
    print("=" * 60)
    
    batch_size = 30
    total_success = 0
    total_fail = 0
    
    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total + batch_size - 1) // batch_size
        
        print(f"\n🔄 배치 {batch_num}/{total_batches} ({len(batch)}건)")
        
        success, fail = process_batch(batch)
        total_success += success
        total_fail += fail
        
        # 진행률
        progress = min((i + batch_size) / total * 100, 100)
        print(f"\n  진행률: {progress:.1f}% (성공: {total_success}, 실패: {total_fail})")
    
    # 5. 최종 결과
    print("\n" + "=" * 60)
    print("🎉 완료!")
    print("=" * 60)
    
    print(f"\n📊 이번 실행:")
    print(f"   성공: {total_success}건")
    print(f"   실패: {total_fail}건")
    print(f"   총: {total}건")
    
    # 최종 통계
    print("\n📊 최종 상태:")
    stats = get_stats()
    if stats:
        print(f"   총 레코드: {stats.get('total_records', 0)}건")
        print(f"   임베딩 완료: {stats.get('embedded_records', 0)}건 ({stats.get('completion_percentage', 0)}%)")
        print(f"   대기 중: {stats.get('pending_records', 0)}건")


if __name__ == "__main__":
    main()
