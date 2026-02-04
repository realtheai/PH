"""
Supabase 테이블 생성 및 pgvector 설정
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

def setup_supabase():
    """Supabase 테이블 및 Vector 확장 설정"""
    
    print("=" * 60)
    print("Supabase 테이블 생성 및 Vector 설정")
    print("=" * 60)
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # SQL 파일 읽기
    print("\n1️⃣  기본 스키마 실행...")
    with open('database/schema.sql', 'r', encoding='utf-8') as f:
        base_schema = f.read()
    
    print("2️⃣  Vector 스키마 실행...")
    with open('database/schema_vector.sql', 'r', encoding='utf-8') as f:
        vector_schema = f.read()
    
    # Supabase SQL Editor를 통해 실행해야 함
    print("\n⚠️  중요: Supabase Dashboard에서 직접 실행 필요!")
    print("\n다음 단계:")
    print("1. Supabase Dashboard 열기: https://app.supabase.com")
    print("2. SQL Editor로 이동")
    print("3. 아래 SQL 실행:")
    print("\n" + "=" * 60)
    print("-- Step 1: 기본 테이블 생성")
    print("=" * 60)
    print(base_schema[:500] + "...\n")
    
    print("=" * 60)
    print("-- Step 2: pgvector 확장 추가")
    print("=" * 60)
    print(vector_schema[:500] + "...")
    
    print("\n" + "=" * 60)
    print("또는 Supabase CLI 사용:")
    print("=" * 60)
    print(f"supabase db push --db-url {SUPABASE_URL}")
    
    # 테이블 존재 여부 확인
    print("\n" + "=" * 60)
    print("테이블 확인...")
    print("=" * 60)
    
    try:
        # phishing_news 테이블 확인
        result = supabase.table('phishing_news').select('id', count='exact').limit(1).execute()
        print(f"✅ phishing_news 테이블 존재 (레코드 수: {result.count})")
    except Exception as e:
        print(f"❌ phishing_news 테이블 없음: {e}")
    
    try:
        # phishing_images 테이블 확인
        result = supabase.table('phishing_images').select('id', count='exact').limit(1).execute()
        print(f"✅ phishing_images 테이블 존재 (레코드 수: {result.count})")
    except Exception as e:
        print(f"❌ phishing_images 테이블 없음: {e}")
    
    try:
        # phishing_stats 테이블 확인
        result = supabase.table('phishing_stats').select('id', count='exact').limit(1).execute()
        print(f"✅ phishing_stats 테이블 존재 (레코드 수: {result.count})")
    except Exception as e:
        print(f"❌ phishing_stats 테이블 없음: {e}")


if __name__ == "__main__":
    setup_supabase()
