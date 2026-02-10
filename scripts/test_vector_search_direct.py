"""
Vector Search 직접 테스트 (RPC 우회, 직접 쿼리)
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

def search_news(embedding, limit=5):
    """뉴스에서 직접 검색"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # 뉴스 검색 (classification 필터 + 임베딩 있는 것만)
    url = f"{SUPABASE_URL}/rest/v1/phishing_news"
    params = {
        'select': 'id,title,content,translated_content,source,phishing_type,classification,embedding',
        'classification': 'in.(REAL_CASE,NEWS)',
        'embedding': 'not.is.null',
        'limit': str(limit * 3)  # 여유있게 가져오기
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  뉴스 조회 실패: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 뉴스 조회 오류: {e}")
        return []

def search_images(embedding, limit=5):
    """이미지에서 직접 검색"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # 이미지 검색
    url = f"{SUPABASE_URL}/rest/v1/phishing_images"
    params = {
        'select': 'id,ocr_text,translated_text,translated_content,source,phishing_type,classification,embedding',
        'classification': 'in.(REAL_CASE,NEWS)',
        'embedding': 'not.is.null',
        'limit': str(limit * 3)
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  이미지 조회 실패: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 이미지 조회 오류: {e}")
        return []

def calculate_similarity(query_embedding, item_embedding):
    """코사인 유사도 계산 (1 - 거리)"""
    try:
        # 문자열인 경우 파싱
        if isinstance(item_embedding, str):
            import json
            item_embedding = json.loads(item_embedding)
        
        # 리스트가 아니면 실패
        if not isinstance(item_embedding, list):
            return 0.0
        
        # numpy 없이 직접 계산
        dot_product = sum(q * i for q, i in zip(query_embedding, item_embedding))
        query_norm = sum(q * q for q in query_embedding) ** 0.5
        item_norm = sum(i * i for i in item_embedding) ** 0.5
        
        if query_norm == 0 or item_norm == 0:
            return 0.0
        
        # 코사인 유사도 = dot_product / (norm1 * norm2)
        cosine_sim = dot_product / (query_norm * item_norm)
        return cosine_sim
    except Exception as e:
        return 0.0

def test_vector_search():
    """클라이언트 측 벡터 검색 테스트"""
    
    print("=" * 60)
    print("Vector Search 테스트 (클라이언트 측 계산)")
    print("=" * 60)
    
    # 1. 테스트 메시지
    test_message = "긴급! 국세청입니다. 세금 환급이 있습니다"
    print(f"\n테스트 메시지: {test_message}")
    
    # 2. 임베딩 생성
    print("\n임베딩 생성 중...")
    query_embedding = create_embedding(test_message)
    
    if not query_embedding:
        print("❌ 임베딩 생성 실패")
        return
    
    print(f"✅ 임베딩 생성 완료 (차원: {len(query_embedding)})")
    
    # 3. 데이터 가져오기
    print("\n데이터 조회 중...")
    news_items = search_news(query_embedding, limit=100)
    image_items = search_images(query_embedding, limit=100)
    
    print(f"  뉴스: {len(news_items)}개 조회")
    print(f"  이미지: {len(image_items)}개 조회")
    
    # 4. 유사도 계산
    print("\n유사도 계산 중...")
    results = []
    errors = 0
    
    for item in news_items:
        if item.get('embedding'):
            try:
                similarity = calculate_similarity(query_embedding, item['embedding'])
                if similarity > 0.3:  # threshold
                    results.append({
                        'id': item['id'],
                        'source_type': 'news',
                        'title': item.get('title'),
                        'content': item.get('translated_content') or item.get('content'),
                        'source': item.get('source'),
                        'phishing_type': item.get('phishing_type'),
                        'similarity': similarity
                    })
            except Exception as e:
                errors += 1
    
    for item in image_items:
        if item.get('embedding'):
            try:
                similarity = calculate_similarity(query_embedding, item['embedding'])
                if similarity > 0.3:  # threshold
                    results.append({
                        'id': item['id'],
                        'source_type': 'image',
                        'title': None,
                        'content': (
                            item.get('translated_content') or 
                            item.get('translated_text') or 
                            item.get('ocr_text')
                        ),
                        'source': item.get('source'),
                        'phishing_type': item.get('phishing_type'),
                        'similarity': similarity
                    })
            except Exception as e:
                errors += 1
    
    if errors > 0:
        print(f"  ⚠️  {errors}개 항목 유사도 계산 실패")
    
    # 5. 정렬
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    # 6. 결과 출력
    print(f"\n✅ 검색 성공!")
    print(f"유사 사례 수: {len(results)}건 (상위 10개 표시)\n")
    
    if results:
        print("🔍 상위 결과:")
        for i, case in enumerate(results[:10], 1):
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
    
    print(f"\n{'='*60}")
    print(f"⚡ 성능: RPC timeout 없음, 클라이언트 측 계산")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    test_vector_search()
