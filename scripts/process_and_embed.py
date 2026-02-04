"""
데이터 정제 + 임베딩 생성 + Supabase 업로드 (통합 스크립트)

1단계: Raw 데이터 → Gemini로 분류 → REAL_CASE/NEWS/NOISE
2단계: REAL_CASE + NEWS만 선별 (NOISE 제거)
3단계: 선별된 데이터만 임베딩 생성
4단계: Supabase 업로드
"""
import os
import json
import time
import requests
from typing import List, Dict
from datetime import datetime
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

current_key_index = 0

def get_gemini_client():
    """Gemini API 클라이언트 반환 (키 로테이션)"""
    global current_key_index
    api_key = GEMINI_API_KEYS[current_key_index]
    if not api_key:
        current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
        api_key = GEMINI_API_KEYS[current_key_index]
    genai.configure(api_key=api_key)


def classify_content(title: str, content: str) -> str:
    """
    Gemini로 콘텐츠 분류
    
    Returns:
        'REAL_CASE': 실제 피싱 사례, 피해 사례, 적발 사례
        'NEWS': 피싱 예방, 주의보, 일반 뉴스
        'NOISE': 피싱과 무관한 내용
    """
    global current_key_index
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEYS[current_key_index]}"
        
        prompt = f"""다음 뉴스/텍스트를 분류하세요. 정확히 다음 3가지 중 하나만 답변:

- REAL_CASE: 실제 피싱/스미싱 사례, 피해 사례, 적발 사례, 범죄 수법 설명
- NEWS: 피싱 예방 캠페인, 주의보, 통계, 일반 뉴스
- NOISE: 피싱과 무관한 내용, 광고, 다른 주제

제목: {title}
내용: {content[:300]}

분류 (REAL_CASE/NEWS/NOISE 중 하나만):"""
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        
        result_data = response.json()
        category = result_data['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # 정규화
        if 'REAL_CASE' in category:
            return 'REAL_CASE'
        elif 'NEWS' in category:
            return 'NEWS'
        else:
            return 'NOISE'
            
    except Exception as e:
        print(f"⚠️ 분류 실패: {e}")
        
        # API 키 로테이션
        current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
        
        # 폴백: 키워드 기반 간단 분류
        text = (title + ' ' + content).lower()
        if any(kw in text for kw in ['피해', '사례', '적발', '검거', '당했', '범죄', '수법']):
            return 'REAL_CASE'
        elif any(kw in text for kw in ['예방', '캠페인', '주의', '대응', '통계']):
            return 'NEWS'
        else:
            return 'NOISE'


def create_embedding(text: str, retry=3) -> List[float]:
    """
    텍스트를 임베딩 벡터로 변환 (1536차원)
    """
    global current_key_index
    
    # 텍스트 길이 제한
    text = text[:5000]
    
    for attempt in range(retry):
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            
            embedding = result['embedding']
            
            # 1536차원으로 패딩 (Gemini는 768차원)
            if len(embedding) < 1536:
                embedding = embedding + [0.0] * (1536 - len(embedding))
            elif len(embedding) > 1536:
                embedding = embedding[:1536]
            
            return embedding
            
        except Exception as e:
            print(f"임베딩 오류 (시도 {attempt + 1}/{retry}): {e}")
            
            # API 키 로테이션
            current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
            genai.configure(api_key=GEMINI_API_KEYS[current_key_index])
            
            time.sleep(1)
            
            if attempt == retry - 1:
                return None
    
    return None


def load_and_process_data() -> List[Dict]:
    """
    Raw 데이터 로드 + 정제 + 분류
    
    Returns:
        정제된 데이터 리스트 (REAL_CASE + NEWS만)
    """
    print("=" * 60)
    print("1단계: Raw 데이터 로드 및 정제")
    print("=" * 60)
    
    all_data = []
    
    # 네이버 데이터
    print("\n📥 네이버 데이터 로드...")
    with open('data/raw/naver_api_2025-02-01_to_2026-01-31_fixed.json', 'r', encoding='utf-8') as f:
        naver_data = json.load(f)
    
    print(f"   총 {len(naver_data)}건")
    
    for idx, item in enumerate(naver_data, 1):
        if idx % 100 == 0:
            print(f"   [{idx}/{len(naver_data)}] 분류 중...")
        
        category = classify_content(item.get('title', ''), item.get('content', ''))
        
        if category in ['REAL_CASE', 'NEWS']:  # NOISE 제외
            all_data.append({
                'source': 'naver',
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'url': item.get('url', ''),
                'category': category,
                'phishing_type': None,
                'original_language': 'ko',
                'keywords': item.get('extracted_keywords', []),
                'content_length': len(item.get('content', '')),
                'published_at': item.get('date'),
                'crawled_at': item.get('crawled_at'),
            })
        
        # Rate limit
        time.sleep(0.3)
    
    # 구글 데이터
    print("\n📥 구글 데이터 로드...")
    with open('data/raw/google_news_2025-02-01_to_2026-01-31.json', 'r', encoding='utf-8') as f:
        google_data = json.load(f)
    
    print(f"   총 {len(google_data)}건")
    
    for idx, item in enumerate(google_data, 1):
        if idx % 50 == 0:
            print(f"   [{idx}/{len(google_data)}] 분류 중...")
        
        category = classify_content(item.get('title', ''), item.get('content', ''))
        
        if category in ['REAL_CASE', 'NEWS']:
            all_data.append({
                'source': 'google',
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'url': item.get('url', ''),
                'category': category,
                'phishing_type': None,
                'original_language': 'ko',
                'keywords': item.get('extracted_keywords', []),
                'content_length': len(item.get('content', '')),
                'published_at': item.get('date'),
                'crawled_at': item.get('crawled_at'),
            })
        
        time.sleep(0.3)
    
    # Reddit 데이터 (영어이므로 번역 필요 - 일단 스킵)
    print("\n📥 Reddit 데이터 (영어 - 스킵)...")
    
    print(f"\n✅ 정제 완료:")
    print(f"   - 총 입력: 2,712건")
    print(f"   - 정제 후: {len(all_data)}건")
    print(f"   - 제거됨: {2712 - len(all_data)}건 (NOISE)")
    
    # 정제된 데이터 저장
    processed_file = f'data/processed/phishing_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(processed_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 정제된 데이터 저장: {processed_file}")
    
    return all_data


def create_embeddings_and_upload(data: List[Dict], batch_size: int = 30):
    """
    정제된 데이터에 임베딩 추가 + Supabase 업로드
    """
    print("\n" + "=" * 60)
    print("2단계: 임베딩 생성 및 업로드")
    print("=" * 60)
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    get_gemini_client()
    
    total = len(data)
    uploaded = 0
    failed = 0
    skipped = 0
    
    print(f"\n총 {total}건 처리 예정")
    print(f"배치 크기: {batch_size}")
    print(f"예상 소요 시간: {total * 0.5 / 60:.1f}분\n")
    
    for i in range(0, total, batch_size):
        batch = data[i:i + batch_size]
        
        print(f"\n🔄 배치 {i // batch_size + 1}/{(total + batch_size - 1) // batch_size}")
        
        batch_with_embeddings = []
        
        for idx, item in enumerate(batch):
            global_idx = i + idx + 1
            print(f"  [{global_idx}/{total}] 임베딩 생성 중... {item['title'][:30]}...", end='')
            
            # 텍스트 결합
            text = f"{item['title']} {item['content']}"
            text = text[:5000]
            
            # 임베딩 생성
            embedding = create_embedding(text)
            
            if embedding:
                item['embedding'] = embedding
                batch_with_embeddings.append(item)
                print(" ✅")
            else:
                failed += 1
                print(" ❌")
            
            time.sleep(0.5)  # Rate limit
        
        # Supabase 업로드
        if batch_with_embeddings:
            print(f"\n  📤 배치 업로드 중 ({len(batch_with_embeddings)}건)...", end='')
            
            try:
                result = supabase.table('phishing_news').insert(batch_with_embeddings).execute()
                uploaded += len(batch_with_embeddings)
                print(" ✅")
            except Exception as e:
                print(f" ❌ 오류: {e}")
                # 개별 업로드 시도
                for item in batch_with_embeddings:
                    try:
                        supabase.table('phishing_news').insert(item).execute()
                        uploaded += 1
                    except:
                        failed += 1
        
        # 진행률
        progress = (i + batch_size) / total * 100
        print(f"\n  진행률: {progress:.1f}% (성공: {uploaded}, 실패: {failed})")
    
    print("\n" + "=" * 60)
    print("🎉 완료!")
    print("=" * 60)
    print(f"✅ 업로드 성공: {uploaded}건")
    print(f"❌ 실패: {failed}건")
    print(f"📊 총: {total}건")


def main():
    """메인 실행"""
    print("=" * 60)
    print("피싱 데이터 정제 + 임베딩 + 업로드 (통합)")
    print("=" * 60)
    
    # 1단계: 데이터 정제
    processed_data = load_and_process_data()
    
    if not processed_data:
        print("\n❌ 정제된 데이터 없음")
        return
    
    # 확인
    print(f"\n정제된 데이터 {len(processed_data)}건을 임베딩하고 업로드하시겠습니까?")
    print("예상 시간:", len(processed_data) * 0.5 / 60, "분")
    
    response = input("계속 진행? (y/n): ")
    
    if response.lower() == 'y':
        # 2단계: 임베딩 + 업로드
        create_embeddings_and_upload(processed_data, batch_size=30)
    else:
        print("\n취소됨")


if __name__ == "__main__":
    main()
