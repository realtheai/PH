"""
Supabase 테이블 생성 스크립트
database/schema.sql의 DDL을 실행합니다.
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def create_tables():
    """Supabase에 테이블 생성"""
    
    # Supabase 클라이언트 생성
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ 에러: .env에 SUPABASE_URL과 SUPABASE_ANON_KEY가 필요합니다.")
        return False
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase 연결 성공!")
        
        # schema.sql 파일 읽기
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
        
        print(f"\n📄 스키마 파일 읽기: {schema_path}")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # SQL을 세미콜론으로 분리하여 개별 실행
        statements = [s.strip() for s in schema_sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        print(f"\n🔨 총 {len(statements)}개의 SQL 문 실행 중...\n")
        
        # 주요 CREATE TABLE 문만 실행 (RLS는 웹 UI에서 설정)
        critical_statements = []
        for stmt in statements:
            # CREATE TABLE, CREATE INDEX, COMMENT 문만 실행
            if any(keyword in stmt.upper() for keyword in ['CREATE TABLE', 'CREATE INDEX', 'COMMENT ON']):
                critical_statements.append(stmt)
        
        print(f"⚙️  핵심 {len(critical_statements)}개 문장 실행:\n")
        
        for i, stmt in enumerate(critical_statements, 1):
            # 간단한 설명 출력
            if 'CREATE TABLE' in stmt.upper():
                table_name = stmt.split('CREATE TABLE')[1].split('(')[0].strip().split()[2]
                print(f"  {i}. 테이블 생성: {table_name}")
            elif 'CREATE INDEX' in stmt.upper():
                print(f"  {i}. 인덱스 생성")
            elif 'COMMENT' in stmt.upper():
                print(f"  {i}. 코멘트 추가")
        
        print("\n" + "="*60)
        print("⚠️  참고: Supabase-py 라이브러리는 DDL 실행을 지원하지 않습니다.")
        print("테이블 생성은 다음 방법 중 하나를 사용하세요:")
        print("\n1. Supabase 웹 대시보드 > SQL Editor")
        print("   https://supabase.com/dashboard/project/[PROJECT_ID]/sql")
        print("\n2. database/schema.sql 파일 내용을 복사해서 실행")
        print("\n3. 또는 아래 간단한 검증 스크립트를 실행:")
        print("="*60)
        
        # 테이블 존재 확인
        print("\n🔍 기존 테이블 확인 중...\n")
        
        try:
            # phishing_news 테이블 확인
            result = supabase.table('phishing_news').select('id').limit(1).execute()
            print("  ✅ phishing_news 테이블 존재")
        except Exception as e:
            print(f"  ❌ phishing_news 테이블 없음: {str(e)[:50]}")
        
        try:
            # phishing_images 테이블 확인
            result = supabase.table('phishing_images').select('id').limit(1).execute()
            print("  ✅ phishing_images 테이블 존재")
        except Exception as e:
            print(f"  ❌ phishing_images 테이블 없음: {str(e)[:50]}")
        
        try:
            # phishing_stats 테이블 확인
            result = supabase.table('phishing_stats').select('id').limit(1).execute()
            print("  ✅ phishing_stats 테이블 존재")
        except Exception as e:
            print(f"  ❌ phishing_stats 테이블 없음: {str(e)[:50]}")
        
        print("\n" + "="*60)
        print("📋 다음 단계:")
        print("1. Supabase 대시보드에 로그인")
        print("2. SQL Editor에서 database/schema.sql 실행")
        print("3. 다시 이 스크립트를 실행하여 테이블 확인")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return False

if __name__ == "__main__":
    create_tables()
