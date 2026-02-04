"""
Supabase 빠른 설정 (REST API 사용)
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

def create_tables_via_api():
    """REST API로 테이블 생성"""
    
    print("=" * 60)
    print("Supabase 테이블 생성 (REST API)")
    print("=" * 60)
    
    # SQL 명령어들
    sqls = [
        # pgvector 확장 (관리자 권한 필요 - Supabase Dashboard에서 수동 실행)
        """
        Supabase Dashboard > SQL Editor에서 실행 필요:
        
        CREATE EXTENSION IF NOT EXISTS vector;
        """,
        
        # 기본 테이블들은 이미 schema.sql에 정의되어 있음
    ]
    
    print("\n⚠️  Supabase에 SQL 직접 실행이 필요합니다.")
    print("\n📝 다음 URL로 이동하세요:")
    print(f"   {SUPABASE_URL.replace('https://', 'https://app.supabase.com/project/')}/editor")
    
    print("\n📋 SQL Editor에서 아래 SQL을 실행하세요:")
    print("=" * 60)
    
    # schema.sql 읽기
    with open('database/schema.sql', 'r', encoding='utf-8') as f:
        base_schema = f.read()
    
    # schema_vector.sql 읽기
    with open('database/schema_vector.sql', 'r', encoding='utf-8') as f:
        vector_schema = f.read()
    
    print(base_schema)
    print("\n" + "=" * 60)
    print(vector_schema)
    
    print("\n" + "=" * 60)
    print("✅ SQL 복사 완료!")
    print("Supabase Dashboard에서 실행 후 계속 진행하세요.")


if __name__ == "__main__":
    create_tables_via_api()
