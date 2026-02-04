"""
Supabase 테이블 생성 및 Vector 확장 설정
REST API를 사용하여 SQL 실행
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def execute_sql(sql: str):
    """Supabase REST API로 SQL 실행"""
    
    # Supabase Management API 엔드포인트
    # 참고: ANON_KEY로는 직접 SQL 실행 불가능
    # Service Role Key가 필요하거나 Dashboard에서 실행 필요
    
    print("⚠️  Supabase SQL 실행은 Dashboard에서 직접 해야 합니다.")
    print(f"\n📝 다음 URL로 이동하세요:")
    print(f"   https://app.supabase.com/project/wqepkzgehbqrtkrzkimn/editor")
    print("\n" + "=" * 60)
    print(sql)
    print("=" * 60)


def check_tables():
    """테이블 존재 여부 확인"""
    
    print("=" * 60)
    print("Supabase 테이블 확인")
    print("=" * 60)
    
    # REST API로 테이블 조회
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    tables = ['phishing_news', 'phishing_images', 'phishing_stats']
    
    for table in tables:
        url = f"{SUPABASE_URL}/rest/v1/{table}?select=id&limit=1"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {table} 테이블 존재")
            elif response.status_code == 404:
                print(f"❌ {table} 테이블 없음 (생성 필요)")
            else:
                print(f"⚠️  {table} 테이블 상태 불명 (코드: {response.status_code})")
        except Exception as e:
            print(f"❌ {table} 확인 실패: {e}")


def setup():
    """Supabase 설정"""
    
    print("=" * 60)
    print("Supabase Vector Search 설정")
    print("=" * 60)
    
    # 1. 테이블 확인
    check_tables()
    
    print("\n" + "=" * 60)
    print("SQL 실행이 필요합니다")
    print("=" * 60)
    
    # 2. SQL 읽기
    with open('database/schema.sql', 'r', encoding='utf-8') as f:
        base_schema = f.read()
    
    with open('database/schema_vector.sql', 'r', encoding='utf-8') as f:
        vector_schema = f.read()
    
    # 3. SQL 출력
    print("\n📋 Step 1: 기본 테이블 생성")
    print("=" * 60)
    print(base_schema)
    
    print("\n" + "=" * 60)
    print("📋 Step 2: pgvector 확장 추가")
    print("=" * 60)
    print(vector_schema)
    
    # 4. 실행 방법 안내
    print("\n" + "=" * 60)
    print("✅ 다음 단계:")
    print("=" * 60)
    print("1. Supabase Dashboard 열기:")
    print("   https://app.supabase.com/project/wqepkzgehbqrtkrzkimn/editor")
    print("\n2. SQL Editor에서 위 SQL들을 순서대로 실행")
    print("\n3. 실행 완료 후 다음 명령어 실행:")
    print("   python scripts/process_and_embed.py")


if __name__ == "__main__":
    setup()
