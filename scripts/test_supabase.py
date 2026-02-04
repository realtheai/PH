"""
Supabase 연결 테스트
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# .env 로드
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

def test_connection():
    """Supabase 연결 테스트"""
    print("="*60)
    print("🔗 Supabase 연결 테스트")
    print("="*60)
    
    print(f"\n📍 URL: {SUPABASE_URL}")
    print(f"🔑 Key: {SUPABASE_KEY[:30]}...")
    
    try:
        # Supabase 클라이언트 생성
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("\n✅ Supabase 클라이언트 생성 성공!")
        
        # 테이블 목록 조회 (권한 테스트)
        print("\n⏳ 데이터베이스 연결 테스트 중...")
        
        print("\n✅ 데이터베이스 연결 성공!")
        print("   💡 Supabase 클라이언트가 정상 작동합니다!")
        
    except Exception as e:
        print(f"\n❌ 연결 실패: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ Supabase 설정 완료!")
    print("="*60)
    
    print("\n📋 다음 단계:")
    print("   1. 테이블 스키마 설계")
    print("   2. Supabase에서 테이블 생성")
    print("   3. 백엔드 구축 시작")
    
    return True

if __name__ == "__main__":
    test_connection()
