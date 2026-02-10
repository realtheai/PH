"""
Vector Search 직접 테스트 (OpenAI 임베딩 사용)
"""
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def create_embedding(text):
    """OpenAI 임베딩 생성 (1536차원)"""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ 임베딩 생성 오류: {e}")
        return None

def test_vector_search():
    """Vector Search 테스트"""
    
    print("=" * 60)
    print("Vector Search 테스트")
    print("=" * 60)
    
    # 1. 테스트 메시지
    test_message = "긴급! 국세청입니다. 세금 환급이 있습니다"
    print(f"\n테스트 메시지: {test_message}")
    
    # 2. 임베딩 생성
    print("\n임베딩 생성 중...")
    embedding = create_embedding(test_message)
    
    if not embedding:
        print("❌ 임베딩 생성 실패")
        return
    
    print(f"✅ 임베딩 생성 완료 (차원: {len(embedding)})")
    
    # 3. RPC 호출
    print("\nSupabase RPC 호출 중...")
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    rpc_url = f"{SUPABASE_URL}/rest/v1/rpc/find_similar_phishing"
    payload = {
        'query_embedding': embedding,
        'match_threshold': 0.3,  # 30%로 낮춰서 더 많은 결과 검색
        'match_count': 10  # 10개로 증가
    }
    
    try:
        response = requests.post(rpc_url, headers=headers, json=payload, timeout=120)  # 2분으로 증가
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 검색 성공!")
            print(f"유사 사례 수: {len(result) if result else 0}건")
            
            if result:
                print("\n🔍 상위 결과:")
                for i, case in enumerate(result[:5], 1):
                    similarity = case.get('similarity', 0)
                    source_type = case.get('source_type', 'unknown')
                    title = case.get('title') or 'N/A'
                    content = case.get('content') or 'N/A'
                    phishing_type = case.get('phishing_type') or 'N/A'
                    source = case.get('source') or 'N/A'
                    
                    print(f"\n[{i}] 유사도: {similarity:.3f} | 타입: {source_type} | 출처: {source}")
                    if title != 'N/A':
                        print(f"    제목: {title[:80]}")
                    print(f"    내용: {content[:100]}...")
                    print(f"    피싱유형: {phishing_type}")
            else:
                print("\n⚠️  유사 사례를 찾지 못했습니다")
        else:
            print(f"\n❌ 오류: {response.text}")
            
    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")

if __name__ == "__main__":
    test_vector_search()
