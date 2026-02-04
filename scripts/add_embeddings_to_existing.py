"""
기존 Supabase 데이터에 임베딩 추가
embedding이 NULL인 레코드만 처리
"""
import os
import time
from typing import List
from dotenv import load_dotenv
from supabase import create_client, Client
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

def get_gemini_client():
    """Gemini API 초기화"""
    global current_key_index
    api_key = GEMINI_API_KEYS[current_key_index]
    if not api_key:
        current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
        api_key = GEMINI_API_KEYS[current_key_index]
    genai.configure(api_key=api_key)


def create_embedding(text: str, retry=3) -> List[float]:
    """텍스트를 임베딩 벡터로 변환 (1536차원)"""
    global current_key_index
    
    text = text[:5000]  # 최대 5000자
    
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
            print(f"⚠️  임베딩 오류 (시도 {attempt + 1}/{retry}): {e}")
            
            # API 키 로테이션
            current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
            genai.configure(api_key=GEMINI_API_KEYS[current_key_index])
            
            time.sleep(2)
            
            if attempt == retry - 1:
                return None
    
    return None


def process_existing_data(batch_size=30, max_records=None):
    """기존 데이터에 임베딩 추가"""
    
    print("=" * 60)
    print("기존 데이터에 임베딩 추가")
    print("=" * 60)
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    get_gemini_client()
    
    # 1. 통계 확인
    print("\n📊 현재 상태 확인...")
    stats = supabase.table('phishing_embedding_stats').select('*').execute()
    if stats.data:
        stat = stats.data[0]
        print(f"   총 레코드: {stat['total_records']}건")
        print(f"   임베딩 완료: {stat['embedded_records']}건")
        print(f"   대기 중: {stat['pending_records']}건")
        print(f"   완료율: {stat['completion_percentage']}%")
    
    # 2. embedding이 NULL인 레코드 가져오기
    print("\n📥 임베딩 대기 중인 레코드 조회...")
    
    query = supabase.table('phishing_news')\
        .select('id, title, content')\
        .is_('embedding', 'null')\
        .order('id')
    
    if max_records:
        query = query.limit(max_records)
    
    result = query.execute()
    records = result.data
    
    if not records:
        print("✅ 모든 레코드에 임베딩이 이미 있습니다!")
        return
    
    total = len(records)
    print(f"   대기 중인 레코드: {total}건")
    
    # 사용자 확인
    if total > 100:
        print(f"\n⚠️  {total}건의 임베딩 생성 예상 시간: {total * 0.5 / 60:.1f}분")
        response = input("계속 진행하시겠습니까? (y/n): ")
        if response.lower() != 'y':
            print("취소됨")
            return
    
    # 3. 배치 처리
    print(f"\n🚀 임베딩 생성 시작 (배치 크기: {batch_size})")
    
    success_count = 0
    fail_count = 0
    
    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        
        print(f"\n🔄 배치 {i // batch_size + 1}/{(total + batch_size - 1) // batch_size}")
        
        for idx, record in enumerate(batch):
            global_idx = i + idx + 1
            record_id = record['id']
            title = record.get('title', '')
            content = record.get('content', '')
            
            # 제목 미리보기
            preview = title[:40] + "..." if len(title) > 40 else title
            print(f"  [{global_idx}/{total}] {preview}", end=' ')
            
            # 텍스트 결합
            text = f"{title} {content}"
            
            # 임베딩 생성
            embedding = create_embedding(text)
            
            if embedding:
                try:
                    # Supabase 업데이트
                    supabase.table('phishing_news')\
                        .update({'embedding': embedding})\
                        .eq('id', record_id)\
                        .execute()
                    
                    success_count += 1
                    print("✅")
                    
                except Exception as e:
                    fail_count += 1
                    print(f"❌ 업데이트 실패: {e}")
            else:
                fail_count += 1
                print("❌")
            
            # Rate limit
            time.sleep(0.5)
        
        # 진행률
        progress = (i + batch_size) / total * 100
        print(f"\n  진행률: {progress:.1f}% (성공: {success_count}, 실패: {fail_count})")
    
    # 4. 최종 통계
    print("\n" + "=" * 60)
    print("🎉 완료!")
    print("=" * 60)
    
    stats = supabase.table('phishing_embedding_stats').select('*').execute()
    if stats.data:
        stat = stats.data[0]
        print(f"✅ 총 레코드: {stat['total_records']}건")
        print(f"✅ 임베딩 완료: {stat['embedded_records']}건 ({stat['completion_percentage']}%)")
        print(f"⏳ 대기 중: {stat['pending_records']}건")
    
    print(f"\n📊 이번 실행:")
    print(f"   성공: {success_count}건")
    print(f"   실패: {fail_count}건")


def main():
    """메인 실행"""
    print("=" * 60)
    print("기존 Supabase 데이터에 임베딩 추가")
    print("=" * 60)
    
    # 배치 크기와 최대 레코드 설정
    batch_size = 30
    max_records = None  # None이면 전체 처리
    
    # 테스트 모드 (처음 100건만)
    print("\n🧪 모드 선택:")
    print("1. 테스트 (100건만)")
    print("2. 전체 (모든 레코드)")
    
    choice = input("선택 (1/2): ")
    
    if choice == '1':
        max_records = 100
        print("✅ 테스트 모드: 100건만 처리")
    else:
        print("✅ 전체 모드: 모든 레코드 처리")
    
    # 실행
    process_existing_data(batch_size=batch_size, max_records=max_records)


if __name__ == "__main__":
    main()
