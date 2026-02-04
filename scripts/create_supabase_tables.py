"""
Supabase 테이블 자동 생성 스크립트
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

def create_tables():
    """Supabase에 테이블 생성"""
    print("="*60)
    print("🗄️  Supabase 테이블 생성")
    print("="*60)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # SQL 파일 읽기
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("\n📄 SQL 스크립트 로드 완료")
        print(f"   크기: {len(sql_script)} bytes")
        
        print("\n⚠️  주의: Supabase Python SDK는 직접 SQL 실행을 지원하지 않습니다.")
        print("   다음 방법 중 하나를 선택하세요:\n")
        
        print("1️⃣  Supabase 웹 UI에서 실행 (추천)")
        print("   - https://supabase.com/dashboard")
        print("   - SQL Editor → New Query")
        print("   - database/schema.sql 내용 복사 & 붙여넣기")
        print("   - Run 클릭\n")
        
        print("2️⃣  psycopg2로 직접 연결 (고급)")
        print("   - PostgreSQL 연결 문자열 필요")
        print("   - pip install psycopg2-binary")
        
        print("\n" + "="*60)
        print("💡 SQL 파일 위치: database/schema.sql")
        print("="*60)
        
        # 테이블 존재 확인 시도
        print("\n🔍 기존 테이블 확인 중...")
        try:
            # phishing_news 테이블 조회 시도
            result = supabase.table('phishing_news').select("*").limit(1).execute()
            print("✅ phishing_news 테이블이 이미 존재합니다!")
            print(f"   현재 레코드 수: 확인 필요")
        except Exception as e:
            if "does not exist" in str(e).lower():
                print("❌ phishing_news 테이블이 없습니다. 생성 필요!")
            else:
                print(f"⚠️  확인 오류: {e}")
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")

if __name__ == "__main__":
    create_tables()
