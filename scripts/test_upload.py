"""
Supabase 업로드 테스트 (샘플 5개만)
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

def test_upload():
    print("="*60)
    print("🧪 Supabase 업로드 테스트 (샘플 5개)")
    print("="*60)
    
    # Supabase 연결
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase 연결 성공\n")
    
    # 네이버 데이터 로드
    naver_file = 'data/raw/daily/naver_api_20260130_173420.json'
    
    with open(naver_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📄 파일 로드: {naver_file}")
    print(f"   전체 데이터: {len(data)}건")
    print(f"   테스트 데이터: 5건\n")
    
    # 샘플 5개만 선택
    sample_data = data[:5]
    
    success_count = 0
    
    for idx, item in enumerate(sample_data, 1):
        try:
            # 데이터 준비
            upload_data = {
                'source': 'naver',
                'title': item['title'],
                'content': item['content'],
                'url': item['url'],
                'category': 'NEWS',  # 기본값
                'original_language': 'ko',
                'content_length': len(item['content']) if item.get('content') else 0,
                'published_at': item.get('date'),  # 'date' 필드 사용
                'crawled_at': item['crawled_at']
            }
            
            # 중복 확인
            existing = supabase.table('phishing_news').select("id").eq("url", item['url']).execute()
            
            if existing.data:
                print(f"  [{idx}/5] ⚠️  중복 스킵: {item['title'][:30]}...")
                continue
            
            # INSERT
            result = supabase.table('phishing_news').insert(upload_data).execute()
            success_count += 1
            print(f"  [{idx}/5] ✅ 업로드: {item['title'][:30]}...")
            
        except Exception as e:
            print(f"  [{idx}/5] ❌ 오류: {e}")
    
    print(f"\n📊 결과: {success_count}/5 건 업로드 성공")
    
    # 데이터 확인
    print("\n🔍 DB 데이터 확인:")
    result = supabase.table('phishing_news').select("id, source, title").limit(10).execute()
    
    if result.data:
        for row in result.data:
            print(f"   - [{row['source']}] {row['title'][:40]}...")
    else:
        print("   (데이터 없음)")
    
    print("\n" + "="*60)
    print("✅ 테스트 완료!")
    print("="*60)

if __name__ == "__main__":
    test_upload()
