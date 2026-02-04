"""
Vector Search 직접 테스트
"""
import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def create_embedding(text):
    """임베딩 생성"""
    genai.configure(api_key=GEMINI_API_KEY)
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_query"
    )
    embedding = result['embedding']
    if len(embedding) < 1536:
        embedding = embedding + [0.0] * (1536 - len(embedding))
    return embedding

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
        'match_threshold': 0.5,  # 낮춰서 테스트
        'match_count': 5
    }
    
    try:
        response = requests.post(rpc_url, headers=headers, json=payload, timeout=15)
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 검색 성공!")
            print(f"유사 사례 수: {len(result) if result else 0}건")
            
            if result:
                print("\n🔍 상위 3개 결과:")
                for i, case in enumerate(result[:3], 1):
                    print(f"\n[{i}] 유사도: {case.get('similarity', 0):.3f}")
                    print(f"    제목: {case.get('title', '')[:50]}...")
            else:
                print("\n⚠️  유사 사례를 찾지 못했습니다")
        else:
            print(f"\n❌ 오류: {response.text}")
            
    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")

if __name__ == "__main__":
    test_vector_search()
