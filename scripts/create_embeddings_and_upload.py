"""
피싱 데이터 임베딩 생성 및 Supabase 업로드
Gemini API를 사용하여 텍스트를 임베딩 벡터로 변환
"""
import os
import json
import time
from typing import List, Dict
from dotenv import load_dotenv
from supabase import create_client, Client
import google.generativeai as genai

load_dotenv()

# 환경 변수
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

# 현재 사용 중인 API 키 인덱스
current_key_index = 0

def get_gemini_client():
    """Gemini API 클라이언트 반환 (키 로테이션)"""
    global current_key_index
    api_key = GEMINI_API_KEYS[current_key_index]
    genai.configure(api_key=api_key)
    return genai


def create_embedding(text: str, retry=3) -> List[float]:
    """
    텍스트를 임베딩 벡터로 변환
    
    Args:
        text: 임베딩할 텍스트
        retry: 재시도 횟수
    
    Returns:
        1536차원 임베딩 벡터
    """
    global current_key_index
    
    for attempt in range(retry):
        try:
            # Gemini embedding 생성
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            
            embedding = result['embedding']
            
            # 1536차원으로 패딩 (Gemini는 768차원이므로)
            if len(embedding) < 1536:
                embedding = embedding + [0.0] * (1536 - len(embedding))
            elif len(embedding) > 1536:
                embedding = embedding[:1536]
            
            return embedding
            
        except Exception as e:
            print(f"임베딩 생성 오류 (시도 {attempt + 1}/{retry}): {e}")
            
            # API 키 로테이션
            current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
            genai.configure(api_key=GEMINI_API_KEYS[current_key_index])
            
            # 재시도 전 대기
            time.sleep(2)
            
            if attempt == retry - 1:
                print(f"임베딩 생성 실패: {text[:100]}")
                return None


def load_phishing_data() -> List[Dict]:
    """피싱 데이터 로드"""
    data = []
    
    # 네이버 데이터
    print("📥 네이버 데이터 로드...")
    with open('data/raw/naver_api_2025-02-01_to_2026-01-31_fixed.json', 'r', encoding='utf-8') as f:
        naver_data = json.load(f)
        for item in naver_data:
            data.append({
                'source': 'naver',
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'url': item.get('url', ''),
                'phishing_type': None,  # 나중에 분류
                'keywords': item.get('extracted_keywords', []),
                'published_at': item.get('date'),
                'crawled_at': item.get('crawled_at'),
            })
    
    # 구글 데이터
    print("📥 구글 데이터 로드...")
    with open('data/raw/google_news_2025-02-01_to_2026-01-31.json', 'r', encoding='utf-8') as f:
        google_data = json.load(f)
        for item in google_data:
            data.append({
                'source': 'google',
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'url': item.get('url', ''),
                'phishing_type': None,
                'keywords': item.get('extracted_keywords', []),
                'published_at': item.get('date'),
                'crawled_at': item.get('crawled_at'),
            })
    
    # Reddit 데이터
    print("📥 Reddit 데이터 로드...")
    with open('data/raw/reddit_2025-02-01_to_2026-01-31.json', 'r', encoding='utf-8') as f:
        reddit_data = json.load(f)
        for item in reddit_data:
            data.append({
                'source': 'reddit',
                'title': item.get('title', ''),
                'content': item.get('content', '') or item.get('selftext', ''),
                'url': item.get('url', ''),
                'phishing_type': None,
                'keywords': item.get('extracted_keywords', []),
                'published_at': item.get('created_utc'),
                'crawled_at': item.get('crawled_at'),
            })
    
    print(f"✅ 총 {len(data)}건의 데이터 로드 완료")
    return data


def upload_to_supabase(data: List[Dict], batch_size: int = 50):
    """
    Supabase에 데이터 업로드 (임베딩 포함)
    
    Args:
        data: 업로드할 데이터 리스트
        batch_size: 배치 크기
    """
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    total = len(data)
    uploaded = 0
    failed = 0
    
    print(f"\n📤 Supabase 업로드 시작 (총 {total}건)")
    print(f"배치 크기: {batch_size}")
    
    for i in range(0, total, batch_size):
        batch = data[i:i + batch_size]
        
        # 임베딩 생성
        print(f"\n🔄 배치 {i // batch_size + 1}/{(total + batch_size - 1) // batch_size}")
        
        batch_with_embeddings = []
        for idx, item in enumerate(batch):
            print(f"  [{i + idx + 1}/{total}] 임베딩 생성 중...", end='\r')
            
            # 텍스트 결합 (제목 + 내용)
            text = f"{item['title']} {item['content']}"
            text = text[:5000]  # 최대 5000자
            
            # 임베딩 생성
            embedding = create_embedding(text)
            
            if embedding:
                item['embedding'] = embedding
                item['content_length'] = len(item['content'])
                batch_with_embeddings.append(item)
            else:
                failed += 1
            
            # Rate limit 방지
            time.sleep(0.5)
        
        # Supabase 업로드
        try:
            result = supabase.table('phishing_news').insert(batch_with_embeddings).execute()
            uploaded += len(batch_with_embeddings)
            print(f"  ✅ 배치 업로드 완료 ({len(batch_with_embeddings)}건)")
        except Exception as e:
            print(f"  ❌ 배치 업로드 실패: {e}")
            failed += len(batch_with_embeddings)
        
        # 진행률 표시
        progress = (i + batch_size) / total * 100
        print(f"진행률: {progress:.1f}% (성공: {uploaded}, 실패: {failed})")
    
    print(f"\n🎉 업로드 완료!")
    print(f"  - 성공: {uploaded}건")
    print(f"  - 실패: {failed}건")
    print(f"  - 총: {total}건")


def main():
    """메인 실행"""
    print("=" * 60)
    print("피싱 데이터 임베딩 생성 및 업로드")
    print("=" * 60)
    
    # Gemini API 초기화
    get_gemini_client()
    
    # 데이터 로드
    data = load_phishing_data()
    
    # 샘플 테스트 (처음 5개만)
    print("\n🧪 샘플 테스트 (5건)...")
    sample_data = data[:5]
    
    for i, item in enumerate(sample_data):
        text = f"{item['title']} {item['content']}"[:200]
        print(f"\n[{i + 1}] {text}...")
        
        embedding = create_embedding(text)
        if embedding:
            print(f"  ✅ 임베딩 생성 성공 (차원: {len(embedding)})")
        else:
            print(f"  ❌ 임베딩 생성 실패")
    
    # 전체 업로드 진행 여부 확인
    response = input(f"\n전체 {len(data)}건을 업로드하시겠습니까? (y/n): ")
    
    if response.lower() == 'y':
        upload_to_supabase(data, batch_size=50)
    else:
        print("업로드 취소됨")


if __name__ == "__main__":
    main()
